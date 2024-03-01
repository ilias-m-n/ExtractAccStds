import os
import re
from tiktoken import get_encoding
from openai import OpenAI

def replace_consecutive_newlines(text) -> str:
    # Use regular expression to replace consecutive newlines with a single newline
    modified_text = re.sub(r'\n\s*\n*', ' ', text)
    return modified_text

def remove_special_characters(text) -> str:
    # Use replace to remove \x0c
    modified_text = re.sub(r'[\x0c\xad]', ' ', text)
    return modified_text

def remove_links(text) -> str:
    # Use regular expression to remove links starting with www.
    # Use regular expression to remove links
    modified_text = re.sub(r'http[s]?://[^\s]+|www\.[^\s]+', ' ', text)
    return modified_text

def remove_dates(text) -> str:
    # Use regular expression to remove dates like "31 March 2006"
    modified_text = re.sub(r'\b\d{1,2} [a-zA-Z]+ \d{4}\b', ' ', text)
    return modified_text

def remove_currency(text) -> str:
    modified_text = re.sub(r'[$€£¥₹₽₩₺₴₭₪₨]', " ", text)
    return modified_text

def remove_decimal_numbers(text) -> str:
    # Use regular expression to remove decimal point numbers, sometimes followed by "p" for percent
    modified_text = re.sub(r'\b[(]?(\d{1,3},)*\d{0,3}.\d+[pkKmMbB)]?\b', ' ', text)
    return modified_text

def remove_parenthesis(text) -> str:
    modified_text = re.sub(r'\(\s*\d*[a-zA-Z]?\+?\s*\)', ' ', text)
    return modified_text

def remove_percent(text) -> str:
    # Use regular expression to remove "per cent" text and percent symbols
    modified_text = re.sub(r'\b(?:per cent|%)\b', ' ', text)
    return modified_text

def remove_lonely_symbols(text) -> str:
    modified_text = re.sub(r"\s{1,}(\(?\d{0,2}%[),]?|\'|N/A|\(|p|per cent|\*|·|million|,|\.|-|:)\s{1,}", ' ', text)
    return modified_text

def remove_extra_spaces(text) -> str:
    # Use regular expression to remove extra spaces
    modified_text = re.sub(r'\s+', ' ', text)
    return modified_text.strip()

def remove_extra_points(text) -> str:
    modified_text = re.sub(r'\.{2,}', "\.", text)
    return modified_text

def remove_double_backslashes(text):
    # Use regular expression to remove double backslashes
    modified_text = re.sub(r'[\\]', '', text)
    return modified_text

def remove_emails(text):
    # Use regular expression to remove email addresses
    modified_text = re.sub(r'\S+@\S+', '', text)
    return modified_text

def clean_text(text) -> str:
    text = remove_special_characters(text)
    text = replace_consecutive_newlines(text)
    text = remove_links(text)
    text = remove_dates(text)
    text = remove_currency(text)
    text = remove_decimal_numbers(text)
    text = remove_parenthesis(text)
    text = remove_lonely_symbols(text)
    text = remove_extra_spaces(text)
    text = remove_extra_points(text)
    text = remove_double_backslashes(text)
    text = remove_emails(text)
    return text

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

def count_tokens(text : str, encoding :str = "cl100k_base") -> int:
    encoding = get_encoding(encoding)
    return len(encoding.encode(text))

def get_completion(client : OpenAI, messages : dict[str,str], prompt : str, model : str = "gpt-3.5-turbo-0125", temp = 0):
    return = client.chat.completions.create(model=model,
                                            messages=messages,
                                            temperature=temp,)






