import os
import json
import re
from math import ceil
import pandas as pd
import numpy as np
from collections import Counter
from tiktoken import get_encoding
from openai import OpenAI
from datetime import datetime
from tenacity import (
    retry, 
    stop_after_attempt,
    wait_random_exponential,
)
from . import text_cleaning as tc


# Estimates for pricing and compute time
def calc_price_gpt(num_files, avg_tok_size, num_segments, price, tokens_per_price = 1000):
    price = num_files * num_segments * avg_tok_size / tokens_per_price * price
    return {"$ (excl. VAT)":price}

def calc_compute_time(num_files, avg_tok_size, num_segments, tokens_per_minute):
    min_raw = num_files * avg_tok_size * num_segments / tokens_per_minute
    days = min_raw // (60 * 24)
    hours = (min_raw - days * (60 * 24)) // 60
    min = min_raw % 60
    
    return {'days':days, 'hours':hours, 'min':min, 'raw min':min_raw}

# Estimate for token number
def count_tokens(text : str, encoding :str = "cl100k_base") -> int:
    encoding = get_encoding(encoding)
    return len(encoding.encode(text))

# Read text and check for empty files
def parse_txt(file_path : str) -> str:
    res = None
    # first check whether file exists
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as file:
                res = file.read()
        except UnicodeDecodeError:
            return None
        else:
            # checks whether text contains words temporary solution
            # data should be cleaned before creating datasets
            pattern = re.compile(r'\w+')
            if not bool(re.search(pattern, res)):
                return None
    return res

# Prep Inputs
def prep_inputs(raw_df, filepath_col, id_col, coi, base_token_length, flag_segment, max_token_num, overlay, encoding = "cl100k_base"):

    input_df = raw_df[coi].copy().drop_duplicates()
    input_df['prompt'] = input_df[filepath_col].apply(parse_txt).apply(tc.clean_text)
    input_df['prompt_tokens'] = input_df['prompt'].apply(count_tokens)
    input_df['total_tokens'] = input_df['prompt_tokens'] + base_token_length

    if flag_segment:
        input_df = segment_text_column(input_df, id_col, max_token_num, overlay, base_token_length, encoding)

    return input_df


# Create overlaying segments for text
def segment_text_column(raw_df, id_col, max_tokens, overlay, context_num_tokens, encoding):

    result_df = pd.DataFrame()
    raw_df = raw_df.copy()
    
    for index in raw_df.index:
        row = raw_df.loc[index].copy()
        prompt = raw_df.loc[index]['prompt']
        raw_df.drop(index, inplace = True)

        segments = segment_text(prompt, max_tokens-context_num_tokens, overlay, encoding)
        
        for i, s in enumerate(segments):
            i_row = row.copy()
            i_row["segment"] = str(i)
            i_row["prompt"] = s
            i_row = pd.DataFrame([i_row])
            result_df = pd.concat([result_df, i_row], ignore_index=True)

    result_df["prompt_tokens"] = result_df["prompt"].apply(count_tokens)
    result_df["total_tokens"] = result_df["prompt_tokens"] + context_num_tokens

    return result_df

def segment_text(text, max_tokens, overlay, encoding :str = "cl100k_base"):
    tokens_ = 0
    indexes = []
    text_token_len = count_tokens(text)
    while tokens_ + max_tokens <= text_token_len:
        indexes.append((tokens_, max_tokens+tokens_))
        tokens_ += max_tokens - overlay
    indexes.append((tokens_, text_token_len))

    encoder = get_encoding(encoding)
    encoded_text = encoder.encode(text)
        
    segments = [encoder.decode(encoded_text[index[0]:index[1]]) for index in indexes]    

    return segments

# Commonly used terms section
def det_commonly_used_terms(terms : pd.Series, delimiter = "|", min_ratio : float = .40) -> dict[str,int]:
    res = []
    for items in terms.dropna().values:
        for item in items.split(delimiter):
            if item == "":
                continue
            res.append(item)
    return {k:v for k,v in Counter(res).items() if v >= terms.size * min_ratio}


def concat_terms(terms : dict[str,int], delimiter = " - ") -> str:
    return delimiter.join(list(terms.keys()))


#Call API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(client : OpenAI, messages : dict[str,str], model : str = "gpt-3.5-turbo-0125", temp = 0):
    """
    # Available Models: https://platform.openai.com/docs/models/overview
    
    # Model Response: GPT models return a status code with one of four values, documented in the Response format section of the Chat documentation.
        
        stop: API returned complete model output
        length: Incomplete model output due to max_tokens parameter or token limit
        content_filter: Omitted content due to a flag from our content filters
        null: API response still in progress or incompleteplete
            
        -> response.choices[0].finish_reason
    """
    response = client.chat.completions.create(model=model, messages=messages, temperature=temp)
    return response


def create_messages_context_gpt(system : str, prompt : str, user_assistant : list[tuple[str,str]] = None):
    """
    # Message Types
        - system: messages describe the behavior of the AI assistant. A useful system message for data science use cases is "You are a helpful assistant who
          understands data science."
        - user: messages describe what you want the AI assistant to say. We'll cover examples of user messages throughout this tutorial
        - assistant messages describe previous responses in the conversation. We'll cover how to have an interactive conversation in later tasks

    The first message should be a system message. Additional messages should alternate between the user and the assistant.
    """

    messages = [{"role": "system", "content": system},]

    if user_assistant:
        for example in user_assistant:
            user, assistant = example
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": prompt})

    return messages

def prompt_gpt(client : OpenAI, 
               system : str, 
               prompt : str, 
               user_assistant : list[tuple[str,str]] = None, 
               model : str = "gpt-3.5-turbo-0125", 
               temp = 0):

    messages = create_messages_context_gpt(system, prompt, user_assistant)
    output = get_completion(client, messages, model, temp)
    return output


# FewShot Examples
def prep_fs_examples(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence, flag_UA, flag_segmented, base_prompt=""):
    user_assistant = None
    prompt_examples = ""

    if flag_UA:
        if not flag_segmented:
            user_assistant = get_user_assistant_context(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence)
        else:
            user_assistant = get_user_assistant_context_segmented(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence)
    else:
        if not flag_segmented:
            prompt_examples = get_examples_prompt(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence, base_prompt)
        else:
            prompt_examples = get_examples_prompt_segmented(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence, base_prompt)

    return user_assistant, prompt_examples
    


def get_user_assistant_context(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence):
    user_assistant = []
    
    for id in df[id_col].unique():
        user_content = ""
        assistant_content = {}
        row = df[df[id_col] == id]

        for source in row[source_col].unique():
            user_content += str(row[row[source_col] == source][paragraph_col].values[0]) + " ... "
            if incl_sentence:
                assistant_content[source] = {"sentence": str(row[row[source_col] == source][sentence_col].values[0]),
                                             "term": str(row[row[source_col] == source][standard_col].values[0])}
            else:
                assistant_content[source] = {"term": str(row[row[source_col] == source][standard_col].values[0])}

        user_assistant.append((user_content, json.dumps(assistant_content)))
        
    return user_assistant

def get_user_assistant_context_segmented(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence):
    user_assistant = []

    for i, row in enumerate(df.index):
        paragraph = df.loc[row, paragraph_col]
        source = df.loc[row, source_col]
        sentence_std = df.loc[row, sentence_col]
        standard_std = df.loc[row, standard_col]
        
        assistant_content = {} 

        if incl_sentence:
            assistant_content[source] = {"sentence": sentence_std,
                                         "term": standard_std}
        else:
            assistant_content[source] = {"term": standard_std}

        user_assistant.append((paragraph, json.dumps(assistant_content)))

    return user_assistant


def get_examples_prompt(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence, base):

    examples = base

    for i, id in enumerate(df[id_col].unique()):
        examples += "\nExample " + str(i) + ":\n"
        paragraph = ""
        sentence_std = {}
        row = df[df[id_col] == id]

        for source in row[source_col].unique():            
            paragraph += str(row[row[source_col] == source][paragraph_col].values[0]) + " ... "
            if incl_sentence:
                sentence_std[source] = {"sentence": str(row[row[source_col] == source][sentence_col].values[0]),
                                        "term": str(row[row[source_col] == source][standard_col].values[0])}
            else:
                sentence_std[source] = {"term": str(row[row[source_col] == source][standard_col].values[0])}
        
        examples += paragraph + "\nAnswer " + str(i) + ":\n"
        examples += json.dumps(sentence_std) + '\n'

    return examples

def get_examples_prompt_segmented(df, id_col, source_col, paragraph_col, sentence_col, standard_col, incl_sentence, base):

    examples = base

    for i, row in enumerate(df.index):
        
        examples += "\nExample " + str(i) + ":\n"
        
        paragraph = df.loc[row, paragraph_col]

        source = df.loc[row, source_col]
        sentence_std = df.loc[row, sentence_col]
        standard_std = df.loc[row, standard_col]

        if incl_sentence:
            sentence_std = {source: {"sentence": sentence_std,
                                     "term": standard_std}}
        else:
            sentence_std = {source: {"term": standard_std}}
            
        examples += paragraph + "\nAnswer " + str(i) + ":\n"
        examples += json.dumps(sentence_std) + '\n'

    return examples




'cc_iso3 filename sentence term source found_sentence found_term'
    





