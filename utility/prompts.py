prompt_initial_try = """
Your task is to extract  information from a provided financial statement text. \
More Specifically you are tasked to extract according to or in compliance with what accounting standard \
the financial statement has been prepared. It is possible that a financial statement has \
been constructed in accordance with more than one standard. Make sure you find all that apply. \
They should be mentioned right after each other.

I will provide you with a long text sequence and you should respond with the \
specific wording applied in the text.

I provide you with a segment delimited by tags (<text>, <\text>) and you should extract the desired information.
Only answer with word sequences you find in the provided delimited text!

Here is an example text from which you would be expected to extract one item:

Answer: International Financial Reporting Standards as adopted by the European Union

Text: 2 Summary of significant accounting policies The principal accounting policies applied \
in the preparation of these consolidated financial statements are set out below. These \
policies have been consistently applied to all the years presented, unless otherwise \
stated.\n2.1 Basis of preparation The consolidated financial statements of Anglo Pacific \
Group PLC have been prepared in accordance with International Financial Reporting Standards \
as adopted by the European Union (IFRSs as adopted by the EU), IFRIC interpretations and the \
Companies Act 2006 (United Kingdom) applicable to companies reporting under IFRS. The \
consolidated financial statements have been prepared under the historical cost convention, \
as modified by the revaluation of coal royalties, available-for-sale financial assets, and \
financial assets and financial liabilities (including derivative instruments) at fair value \
through profit or loss.\nThe preparation of financial statements in conformity with IFRS requires \
the use of certain critical accounting estimates. It also requires management to exercise its judgement \
in the process of applying the Group's accounting policies. The areas involving a higher degree of judgement \
or complexity, or areas where assumptions and estimates are significant to the consolidated financial \
statements are disclosed in note 4.\n2.1.1 Changes in accounting policies and disclosures (a) New and amended standards adopted by the Group

Here is another example from which you would be able to extract two items:

Answer:  Australian Accounting Standards
Answer:  International Financial Reporting Standards

Text: In conducting our audit, we have complied with the independence requirements of the Corporations Act 2001. We confirm\
that the independence declaration required by the Corporations Act 2001, which has been given to the directors of Nevada Iron\
Limited, would be in the same terms if given to the directors as at the time of this auditor's report.\nOpinion\nIn our\
opinion:\n(a) the financial report of Nevada Iron Limited is in accordance with the Corporations Act 2001, including:\n(i)\
giving a true and fair view of the consolidated entity's financial position as at 30 June 2015 and of its performance for\
the year ended on that date; and\n(ii) complying with Australian Accounting Standards and the Corporations Regulations 2001;\
and\n(b) the financial report also complies with International Financial Reporting Standards as disclosed in Note 2.\nEmphasis\
of Matter\nAs disclosed in the financial statements, the Company and consolidated entity had net current liabilities of $621,730\
and $1,563,984 at 30 June 2015, respectively, and incurred net after tax losses of $24,943,785 and $29,669,696, respectively,\
and the consolidated entity had net operating cash outflows of $778,045 and net cash outflows of $2,862,345 for the year then ended.\
These conditions, along with other matters as set forth in Note 2, indicate the existence of a material uncertainty which may cast\
significant doubt about the Company and consolidated entity's ability to continue as going concerns and therefore, the Company and\
consolidated entity may be unable to realise their assets and discharge their liabilities in the normal course of business.\nReport on\
the Remuneration Report\nWe have audited the Remuneration Report contained within the directors' report for the year ended 30 June 2015.\
The directors of the company are responsible for the preparation and presentation of the Remuneration Report in accordance with section\
300A of the Corporations Act 2001. Our responsibility is to express an opinion on the Remuneration Report, based on our audit conducted\
in accordance with Australian Auditing Standards.\nOpinion\nIn our opinion the Remuneration Report of Nevada Iron Limited for the year\
ended 30 June 2015 complies with section 300A of the Corporations Act 2001.\nRSM BIRD CAMERON PARTNERS


<text>{cleaned_text}<\text>
"""



# System Context Messages:
system_context_basic = "You are a financial accountant."

system_context_full_task = """
You are a adapt financial accountant. \
You are tasked to extract information contained within two sections, the auditor section and the notes section,  \
of a provided financial statement. \
More specifically, from the notes section you are tasked to extract according to what accounting standard \
the financial statement has been prepared, and from the auditor section you are tasked to extract what accounting \
standard the financial statement is in compliance with. \
It is possible that a financial statement is in compliance with or has been constructed according to multiple \
standards, in which case you should extract both - note, double standards are most likely in close vicinity to each other. \
I will provide you with long textual sequences and you should respond only with the specific wording you find within \
a prompted financial statement.
"""

# Accounting Standards, common terms:
common_terms_accounting_stds = """
Here are a few example, delimited tags (<acc_std><\acc_std>) and separated by dashes, of how accounting standards can be presented in text: \
<acc_std>{acc_std}<\acc_std>.
"""

# Template to present commont terms in denoting section belonging
## please use {terms_audtior} to place terms
common_terms_section_auditor = """
For the auditor part you will most likely find some of these terms, delimited by tags (<auditor><\auditor>) \
and separated by commas, in the vicinity of the information to be extracted: <auditor>{terms_auditor}<\auditor>."""

## please use {terms_notes} to place terms
common_terms_section_notes = """
Within the notes part you will most likely find some of these terms, delimited by tags (<notes><\notes>) \
and separated by commas, in the vicinity of the information to be extracted: <notes>{terms_notes}<\notes>."""

# Answer styles

standard_answer = """
Please only answer with the following format:
Notes: 'information extracted from notes part'
Audit: 'information extracted from audit part'"""
