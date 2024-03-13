


# System Context Messages   ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 
system_context_basic = """
You are a financial accountant.
"""

# Few Shot Examples
examples_base1 = """
Here are a few examples:
"""

# Task Description :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

task_descr_1 = """
You are tasked to extract information contained within two sections, the auditor section and the notes section,  \
of a provided financial statement. \
More specifically, from the notes section you are tasked to extract according to what accounting standard \
the financial statement has been prepared, and from the auditor section you are tasked to extract what accounting \
standard the financial statement is in compliance with. \
It is possible that a financial statement is in compliance with or has been constructed according to multiple \
standards, in which case you should extract both - note, double standards are most likely in close vicinity to each other. \
I will provide you with long textual sequences. Make absolutely sure that you only respond with phrases you find within \
the provided financial statement. \
Before providing an answer, check whether you can find it within the provided text.\n
"""

# Adjustment segmented documents
task_descr_2 = """
You are tasked to extract information from the auditor section and the notes section that can be found within a financial statement document.\
More specifically, from the notes section you are tasked to extract according to what accounting standard \
the financial statement has been prepared, and from the auditor section you are tasked to extract what accounting \
standard the financial statement is in compliance with. \
It is possible that a financial statement is in compliance with or has been constructed according to multiple \
standards, in which case you should extract both - note, double standards are most likely in close vicinity to each other. \
I will provide you with smaller segments from longer textual sequences this means that it is often the case that none of the desired information is contained within one of the segments. 
Make absolutely sure that you only respond with phrases you find within the provided segment of a financial statement. \
Before providing an answer, check whether you can find it within the provided text.\n
"""

# Common Terms :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
## Accounting Standards, common terms:
common_terms_accounting_stds = """
Here are a few examples, delimited tags (<acc_std><\\acc_std>) and separated by dashes, of how accounting standards can be presented in text: \
<acc_std>{acc_std}<\\acc_std>/n.
"""

## Terms commonly found around standard in auditor section
common_terms_section_auditor = """
For the auditor part you will most likely find some of these terms, delimited by tags (<auditor><\\auditor>) \
and separated by commas, in the vicinity of the information to be extracted: <auditor>{terms_auditor}<\\auditor>.
"""

## Terms commonly found around standard in notes section
common_terms_section_notes = """
Within the notes part you will most likely find some of these terms, delimited by tags (<notes><\\notes>) \
and separated by commas, in the vicinity of the information to be extracted: <notes>{terms_notes}<\\notes>.
"""

# Answer styles :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
## Format 1 
answer_format1 = """
Answer in the following format:
{
"notes" : {
    "sentence" : "sentence from which you extracted the standard contained in the notes section",
    "term" : "accounting standard you found in the notes section"},
"audit" : {
    "sentence" : "sentence from which you extracted the standard contained in the auditor section",
    "term" : "accounting standard you found in the auditor section"}
}
"""

## Format 3
answer_format2 = """
Answer in one of the following formats:
- For the audit part:
{
"audit" : {
    "sentence" : "sentence from which you extracted the standard contained in the auditor section",
    "term" : "accounting standard you found in the auditor section"}
}
- For the notes part:
{
"notes" : {
    "sentence" : "sentence from which you extracted the standard contained in the notes section",
    "term" : "accounting standard you found in the notes section"}
}
- In case both parts are in teh same segment:
{
"notes" : {
    "sentence" : "sentence from which you extracted the standard contained in the notes section",
    "term" : "accounting standard you found in the notes section"},
"audit" : {
    "sentence" : "sentence from which you extracted the standard contained in the auditor section",
    "term" : "accounting standard you found in the auditor section"}
}
- In case neither the notes nor the audit section are contained within  the segment:
{
"no info": "no answer"
}
"""

## Format 2
answer_format3 = """
Answer in the following format:
{
"notes" : {"term": accounting standard you found in the notes section},
"audit": {"term": accounting standard extracted from the auditor section}
}
"""

## note segmented
answer_note_seg1 = """
Note in case a segment contains none of the information just answer with: "no info contained".
"""

# Instruction: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
instruction_1 = """ 
Please follow these instructions:
1) First read the financial statement.
2) Second find the sentence that contains the desired term.
3) Extract the desired term.
4) Make sure that the term you extract is acutally contained in the provided financial statement.
5) List both the term and the sentence from which you extracted the term.
"""

instruction_2 = """ 
Please follow these instructions:
1) Read the segment of the financial statement.
2) Identify whether the segment contains the audit part, the notes part, both parts, or neither part.
3) Second find the sentence that contains the desired term and notes whether it is extracted from the \
audit part or the notes part.
4) Extract the desired term.
5) Double check that the term you extract is actually contained in the provided segment.
6) List both the term, the sentence, and what part you extracted the term from.
"""