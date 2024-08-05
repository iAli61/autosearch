# %% [markdown]
# ## Initialize the project 

# %%

from typing import Dict, List, Optional, Union, Callable, Literal
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.formatting_utils import colored
from typing_extensions import Annotated
import autogen
from autogen import Agent
from autogen.token_count_utils import count_token, get_max_token_limit
from autogen.agentchat.contrib.capabilities import transform_messages, transforms

from teachability import Teachability
from concurrent.futures import ThreadPoolExecutor, as_completed

import arxiv

import requests


import os
import shutil
import requests
import pickle
import re
from pathlib import Path

import nest_asyncio
nest_asyncio.apply()

import sqlite3
from utils import *

# %%
print(autogen.__version__)

# %% [markdown]
# ### parameters

# %%
version = "0.0.1"
ProjectID = "polymer_rep"
initiate_db = False

config_file = "OAI_CONFIG_LIST"
max_round = 30
silent = False
recall_threshold = 1.0
# config_file = "OAI_CONFIG_LIST"

topic = "Exploring the Intricacies of Polymer Representation: Unraveling Complexity"

task = """
As a renowned expert, we invite you to contribute a scientifically rigorous article titled, '{topic}'.

Your article should consist of up to seven sections, with a minimum of three dedicated to a detailed examination of technical methodologies. Your expertise will guide readers through the complexities of polymer representation, offering a comprehensive overview of the field's current state and future prospects.

Please structure your article as follows:

Main Tenet: Introduce the core concepts of polymer representation and its significance in the field. Explain the fundamental principles that underpin the representation of polymers and the challenges that researchers face in this domain.

Trailblazing Progress: Explore the most recent advancements in polymer representation, focusing on innovative methodologies and technologies that have revolutionized the field. Discuss the impact of these developments on research and their potential applications in various industries.

Comprehensible Understanding: While your article will be rich with data, ensure that it presents complex concepts in an accessible manner for those outside the field. Use clear language and illustrative examples to enhance comprehension.

Authoritative Sources: Support your discussion with citations from relevant research, studies, and other credible resources that have shaped your understanding. Include these references to assist readers who wish to explore the topics in greater depth.

Current Outlook: Align your insights with the forefront of polymer representation research, highlighting emerging trends and future directions. Discuss the challenges that researchers are currently facing and the opportunities that lie ahead in this dynamic field.

This opportunity allows you to spread knowledge, deepen understanding, and elevate appreciation for ongoing efforts in developing polymer representation. Your contribution will be invaluable in advancing the field and inspiring future generations of researchers.

Should you need additional information, remember to utilize your access to academic resources, including the ability to read summaries and full papers from Arxiv. This tool can significantly enhance your research and enrich your article.
"""


Project_dir = Path(f"./{ProjectID}/{version}")

if not os.path.exists(Project_dir): initiate_db = True

output_dir = f'{Project_dir}/pdf_output'
if not os.path.exists(output_dir): 
    os.makedirs(output_dir)
    os.makedirs(f"{output_dir}/json")
    os.makedirs(f"{output_dir}/markdown")


db_dir = f'{Project_dir}/memo-db/'


if initiate_db:


    if not os.path.exists(Project_dir): 
        shutil.rmtree(Project_dir)
        os.makedirs(Project_dir)
    if os.path.exists(db_dir): shutil.rmtree(db_dir)

    # create a table of papers and abstracts that have been read and saved it in a pickle file
    init_db(Project_dir)

config_list = autogen.config_list_from_json(
    config_file,
    file_location=".",
    filter_dict={
        "model": ["gpt-4-32k", "gpt-4"]#, "gpt4", "gpt-35-turbo-16k", "gpt-4-0613", "gpt-3.5-turbo", "gpt-35-turbo", "gpt-35-turbo-0613"]
    },
)

print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

config_list_32 = autogen.config_list_from_json(
    config_file,
    file_location=".",
    filter_dict={
        "model": ["gpt-4-32k"]#, "gpt4", "gpt-35-turbo-16k", "gpt-4-0613", "gpt-3.5-turbo", "gpt-35-turbo", "gpt-35-turbo-0613"]
    },
)

print("LLM models 32K: ", [config_list_32[i]["model"] for i in range(len(config_list_32))])

# Configuration for the Language Model (LLM)
llm_config = {
    "config_list": config_list,  # config_list should be defined or imported
    "timeout": 120,
    # "seed": 42,
}

# Configuration for the Language Model (LLM)
llm_config_32 = {
    "config_list": config_list_32,  # config_list should be defined or imported
    "timeout": 120,
    # "seed": 42,
}

# Configuration for the manager using the same config_list as llm_config
manager_config = {
    "config_list": config_list,  # config_list should be defined or imported
    "timeout": 60,
    # "seed": 42,
}

# Termination message definition
termination_msg = (
    lambda x: isinstance(x, dict)
    and "TERMINATE" in str(x.get("content", "")).upper()
)



# %% [markdown]
# ## Helper function

# %% [markdown]
# ### database helper function

# %%


# %%


def pdf2md_chunck(url):
    if url[-4:] != ".pdf":
        pdf_filename = url.split('/')[-1] + ".pdf"
    else:
        pdf_filename = url.split('/')[-1]

    if url.startswith("http"):
        pdf_path = os.path.join(output_dir, pdf_filename)
        # Download the PDF
        download_pdf(url, pdf_path)
    else:
        pdf_path = url

    data = analyze_and_save_pdf(f"file://{pdf_path}", f"{output_dir}/json")

    docs, pagecontent, fullmdtext = create_docs(data, 3000, pdf_filename)

    # write fullmdtext to a file
    with open(f"{output_dir}/markdown/{pdf_filename}.md", "w") as f:
        f.write(fullmdtext)

    return docs

url = "https://arxiv.org/pdf/2404.05993v1.pdf"
# docs = pdf2md_chunck(url)


# %% [markdown]
# ## teach agent for some skills

# %%
def create_teachable_groupchat(assitant_name, user_name, db_dir, config_list, verbosity=0):
    
    # Start by instantiating any agent that inherits from ConversableAgent.
    assistant = autogen.ConversableAgent(
        name=assitant_name,  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
    )

    # Instantiate the Teachability capability. Its parameters are all optional.
    teachability = Teachability(
        verbosity=verbosity,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
        reset_db=False,  
        path_to_db_dir=db_dir,
        recall_threshold=1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
    )

    # Now add the Teachability capability to the agent.
    teachability.add_to_agent(assistant)

    user = autogen.UserProxyAgent(
        name=user_name,
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        max_consecutive_auto_reply=0,
        code_execution_config={"use_docker": False},
    )

    return assistant, user

# %%
if initiate_db:
    prompt = "For each memorization task, initiate your process with 'MEMORIZE_ARTICLE:'  \n\n' Delve into the passage to discern and assess its key insights. If the content presents noteworthy information, make a point to memorize these details. Conversely, if the passage does not offer significant insights, there's no need to commit it to memory. Upon choosing to memorize, you MUST finalize your notes by including both the article's title and its URL, employing the format '[source: article_title, article_url]' for efficient future access and verification."

    instract_assistant, instract_user = create_teachable_groupchat("instract_assistant", "instract_user", db_dir, config_list, verbosity=3)

    instract_user.initiate_chat(instract_assistant, silent=True, message=prompt)

# %% [markdown]
# ## Define functions
# 
# ### Arxiv funcs

# %%

text = "Human-Centred Learning Analytics and AI in Education: a Systematic Literature Review"
# arxiv_search(query=text)

# %%


# get_paper_metadata('https://arxiv.org/abs/1810.04805')
# get_paper_metadata('https://arxiv.org/pdf/1810.04805.pdf')
# get_paper_metadata('1810.04805')

# %% [markdown]
# ### arxiv retrieval

# %%
from utils import _arxiv_search

def initiate_chat_with_paper_info(paper, query):

    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user", db_dir, config_list, verbosity=0)
    try:
        arxiver_user.initiate_chat(arxiver,
                        silent=True,
                        message=f"The following article is one of the articles that I found for '{query}' topic: \n\n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummary: {paper.summary} \n?")
        
        add_paper_to_db(paper.pdf_url, "read_abstracts", Project_dir)  # Add paper to the database after initiating the chat
        return f"Title: {paper.title} Authors: {paper.authors} URL: {paper.pdf_url} os added to MEMOS\n\n "
        
    except Exception as e:
        print(f"Error: {e}")

def process_query(query, n_results):
    """Function to process each query and initiate chats for each paper found."""
    papers = _arxiv_search(query, n_results=n_results)

    # check if the abstract has been read before
    papers = [paper for paper in papers if not check_paper_in_db(paper.pdf_url, "read_abstracts", Project_dir)]

    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_with_paper_info, paper, query) for paper in papers]
        for future in as_completed(futures):
            future.result()

def arxiv_retriever(queries: Annotated[List[str], "The list of query texts to search for."], 
                    n_results: Annotated[int, "The number of results to retrieve for each query."] = 10,
                    ) -> str:

    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_query, query_text, n_results) for query_text in queries]
        for future in as_completed(futures):
            future.result()

    # Instantiate a UserProxyAgent to represent the user. But in this notebook, all user input will be simulated.
    return f"Dear Researcher, Database updated with on the following topics: {', '.join(list(queries))}. Please go ahead with your task."
    # return message

# message = ["Large Language Models", "Assessing Language Models", "AI safety and reliability"]
# if initiate_db:
#     arxiv_retriever(message, n_results=10)

# arxiv_retriever(message, n_results=3)

# %% [markdown]
# ### read pdfs

# %%
def check_reasoning(reason, summary):
    
    # Start by instantiating any agent that inherits from ConversableAgent.
    assistant = autogen.AssistantAgent(
        name="reasoning_checker",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
    )

    user = autogen.UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        max_consecutive_auto_reply=0,
        code_execution_config={"use_docker": False},
    )

    chat_hist = user.initiate_chat(assistant, silent=True, message=f"check if \"{reason} is a good reason is to read a paper with the following summary: {summary} /n/n answer only with 'yes' or 'no'")
    return chat_hist.chat_history[-1]['content']

def initiate_chat_read_paper(text, article):
    paper_reader, reader_user = create_teachable_groupchat("paper_reader", "reader_user", db_dir, config_list, verbosity=0)
    try:
        reader_user.initiate_chat(paper_reader,
                        silent=True,
                        message=f"MEMORIZE_ARTICLE: The following passage is extracted from an article titled '{article}': \n\n {text}."
                        )
    except Exception as e:
        print(f"Error: {e}")
        print(colored(f"text: {text}", "red"))
    
def chunk_pdf(url, title):
    
    chunked_elements = pdf2md_chunck(url)

    # find checked_elemnt that includes "REFERENCES" in the second half of the text

    half_length = len(chunked_elements) // 2
    for i, chunk in enumerate(chunked_elements[half_length:], start=half_length):
        chunk_text_upper = chunk.page_content.upper()
        if re.search(r'\bREFERENCE\b', chunk_text_upper) or re.search(r'\bREFERENCES\b', chunk_text_upper):
            # remove the chunck with '\bREFERENCE\b' from chuncked_elements list
            chunked_elements = chunked_elements[:i]
            break

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_read_paper, chunk.page_content, title) for chunk in chunked_elements if len(chunk.page_content.split()) > 30]
        for future in as_completed(futures):
            future.result()

    add_paper_to_db(url, "read_papers", Project_dir)  # Add paper to the database 


"""
This `get_pdfss` function is designed to download a PDF from a given URL, extract its content, 
partition the content into chunks based on titles, and then initiate a chat to share and memorize 
each chunk of the article with a teachable agent and a user.
"""
def get_pdfs(urls: Annotated[List[str], "The list of URLs of the papers to read."],
            reasons: Annotated[List[str], "The list of reasons for reading the papers. it should be same size as urls list."]
            ) -> str:
    
    urls_list = []
    titles_list = []
    message = ''
    for url in urls:

        title, link, updated, summary, pdf_url, paper_id, _ = get_paper_metadata(url)
        
        title = f"{title} [{pdf_url}] updated {updated}"
        
        
        if check_paper_in_db(pdf_url, "read_papers", Project_dir):
            print(f"The article, '{title}', has already been read and shared with you in your memory.")
            message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
            continue
        else:
            if not initiate_db:
                check_reason = check_reasoning(reasons[urls.index(url)], summary)
                if 'no' in check_reason.lower():
                    print(f"The article, '{title}', does not meet the criteria for reading.")
                    message += f"The article, '{title}', does not meet the criteria for reading.\n"
                    continue
            urls_list.append(pdf_url)
            titles_list.append(title)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(chunk_pdf, url, title) for url, title in zip(urls_list, titles_list)]
        for future in as_completed(futures):
            future.result() 

    num_papers = count_papers_in_db("read_papers", Project_dir)
    print(f"{num_papers} articles have been read, so far.")
    message += f"The articles {', and '.join(titles_list)}  has been read and the content has been shared with you in your memory."
    return message

# Example usage
# args = {
# "urls": ["http://arxiv.org/pdf/2305.13267v1", "http://arxiv.org/pdf/2305.06530v1"],
# "reasons": ['factual_check'] * 40
# # ["To understand how the safety performance of LLMs is assessed in typical safety scenarios and instruction attacks.", "To explore the landscape of AI deception focusing on LLMs and the strategies to navigate deceptive behaviors.", "To gain insights into the safety issues, evaluation methods, and enhancement strategies concerning large models.", "To examine the impact of moderation on user enjoyment of AI systems.", "To comprehend methods for robust safety evaluation of LLMs and uncover safety concerns.", "To learn about the reliability of LLMs in generalizability, social biases, calibration, and factuality.", "To uncover the alignment problem in LLMs and its implications for the safety of AI systems.", "To evaluate the safety of VLMs and their vulnerability to jailbreaking attacks.", "To comprehend the framework for evaluating the capability of LLMs in Chinese Journalistic Writing Proficiency and their Safety Adherence.", "To assess the risk taxonomy of AI content and the effectiveness of the AEGIS model.", "To understand how NeuroSymbolic AI approach helps in creating trustworthy AI systems."]
# }
# if initiate_db:
#     for i in range(0, len(args['urls']), 10):
#         get_pdfs(args['urls'][i:i+5], args['reasons'][i:i+5])
        
# get_pdfs(**args)

# %% [markdown]
# ### read pdf

# %%
PartChoice = Literal['summary', 'full']

def _momorized_paper_summary(title, updated, summary, pdf_url, authors):

    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user", db_dir, config_list, verbosity=0)
    try:
        arxiver_user.initiate_chat(arxiver,
                        silent=True,
                        message=f"MEMORIZE_ARTICLE: \n\n '{title}' by {authors} updated on {updated}: {pdf_url} \nsummary: {summary} \n?")
        
        return f"Title: {title} Authors: {authors} URL: {pdf_url} os added to MEMOS\n\n "
    except Exception as e:
        print(f"Error: {e}")

def get_pdf(url: Annotated[str, "The URL of the paper to read."],
            reason: Annotated[str, "reason for reading the paper."],
            part: Annotated[PartChoice, "choose do you need entire paper ('full') or a summary is enough."],
            ) -> str:

    message = ''
    title, link, updated, summary, pdf_url, paper_id, authors= get_paper_metadata(url)

    if part == 'summary':
        _momorized_paper_summary(title, updated, summary, pdf_url, authors)
        return f"Title: {title} Authors: {authors} URL: {pdf_url} \n\n Summary: {summary}"

    title = f"{title} [{pdf_url}] updated {updated}"
        

    if check_paper_in_db(pdf_url, "read_papers", Project_dir):
        print(f"The article, '{title}', has already been read and shared with you in your memory.")
        message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
    else:
        if reason != 'factual_check':
            check_reason = check_reasoning(reason, summary)
            if 'no' in check_reason.lower():
                return f"The article, '{title}', does not meet the criteria for reading."
            
        chunk_pdf(pdf_url, title)

    md_filename = f"{get_paper_id(pdf_url)}.pdf.md"
    md_path = os.path.join(f"{output_dir}/markdown", md_filename)

    with open(md_path, "r") as f:
        content = f.read()

    return content

# Example usage
# get_pdf("http://arxiv.org/pdf/2312.01090v2", "Verify study findings on LLM-based agents in wargames.", "full")


# %% [markdown]
# ### factual check

# %%
def url_check(paper_url: Annotated[str, "The URL of the paper to check."],
            paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
            ):
    if paper_url.find('arxiv.org') == -1:
        return False, f"The provided paper URL, {paper_url}, is not from arxiv.org. Please provide a valid arxiv URL."

    title, link, updated, summary, pdf_url, paper_id, _ = get_paper_metadata(paper_url)
    if title != paper_title:
        return False, f"The provided paper URL, {paper_url}, is not for the paper titled '{paper_title}'. Please provide a valid arxiv URL for the paper."
    
    return True, f"The provided paper URL is from arxiv.org and is for the paper titled '{paper_title}'."

def factual_check(text: Annotated[str, "The writer text to be factually checked."],
                    paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
                    paper_url: Annotated[str, "The arxiv URL of the paper to be used for fact checking."],
                    reason: Annotated[str, "The reason for reading the paper."],
                    paper_authors: Annotated[Optional[str], "The authors of the paper to be used for fact checking."]=None,
                    ) -> str:
    
    url_check_res, message = url_check(paper_url, paper_title)
    if not url_check_res:
        return message

    paper_content = get_pdf(paper_url, reason='factual_check', part='full')

    factual_checker_prompt = """
Below, you will find a passage labeled "TEXT" that references a specific paper: '{paper}' alongside its corresponding "PAPER_CONTENT." Your task is to read the "PAPER_CONTENT" and verify the factual accuracy of the "TEXT" as it pertains to the paper.

Once you have assessed the factual accuracy, you MUST provide feedback, begining with 'FEEDBACK:'. Following your assessment, please write a summary of the paper. Begin this summary with 'Summary of {paper}: '

TEXT:
{text}

PAPER_CONTENT:
{paper_content}
"""

    # Start by instantiating any agent that inherits from ConversableAgent.
    factual_checker = autogen.AssistantAgent(
        name="factual_checker",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
        system_message = "You are a factual_check AI assistant. You are responsible for verifying the factual accuracy of the text provided in relation to the paper content."
        )

    # create a UserProxyAgent instance named "user_proxy"
    factual_checker_user = autogen.UserProxyAgent(
        name="factual_checker_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config=False,
    )

    # let check token limit
    limit = 4096 - 1024
    try:
        limit = get_max_token_limit(factual_checker.llm_config["config_list"][1]["model"]) - 1024  # type: ignore[index]
    except ValueError:
        pass  # limit is unknown
    except TypeError:
        pass  # limit is unknown

    # Limit the token limit per message to avoid exceeding the maximum token limit
    # suppose this capability is not available
    context_handling = transform_messages.TransformMessages(
        transforms=[
            transforms.MessageTokenLimiter(max_tokens=limit, model=factual_checker.llm_config["config_list"][1]["model"]),
        ]
    )
    print(f"factual_check model: {factual_checker.llm_config['config_list'][1]['model']}")
    context_handling.add_to_agent(factual_checker)

    if paper_authors:
        paper = f"{paper_title} [{paper_url}] by {', '.join(list(paper_authors.split(',')))}"
    else:
        paper = f"{paper_title} [{paper_url}]"


    chat = factual_checker_user.initiate_chat(factual_checker, silent=False, max_turns=1,
                                              message=factual_checker_prompt.format(text=text, paper_content=paper_content, paper=paper))

    return chat.chat_history[-1]['content']

args = []
# factual_check(**args[1])

# %% [markdown]
# ## Define Agents

# %% [markdown]
# ## add functions to agents

# %%
funcs = [
    ("arxiv_retriever", arxiv_retriever, "Retrieve summeries of papers from arxiv for give query."),
    ("get_pdfs", get_pdfs, "Retrieve the content of the pdf files from the urls list."),
    ("get_pdf", get_pdf, "Retrieve the content of the pdf file from the url."),
    ("factual_check", factual_check, "Check the factual accuracy of a given text based on a paper."),
    ("arxiv_search", arxiv_search, "retrun the pdf url from arxiv for the given paper title."),
]


def add_func_to_agents(assignments, funcs=funcs):

    # example input 
    # assignments = [(assistants, users, "arxiv_retriever"), (assistants, users, "get_pdfs") ]
    # funcs = [("arxiv_retriever", arxiv_retriever, "Retrieve content for question answering from arxiv."),
    #          ("get_pdfs", get_pdfs, "Retrieve the content of the pdf file from the url.")]

    func_dict = {}
    func_disc_dict = {}
    for func_name, func, func_disc in funcs:
        func_dict[func_name] = func
        func_disc_dict[func_name] = func_disc

    for assignment in assignments:
        caller, executor, func_name = assignment
        autogen.agentchat.register_function(
            func_dict[func_name],
            caller=caller,
            executor=executor,
            name=func_name,
            description=func_disc_dict[func_name]
        )


    return f"Functions {', '.join([func_name for func_name, _, _ in funcs])} are added to the agents."

# %% [markdown]
# ### Write sections

# %%
Section_writer_SP = """
You are now part of a group chat dedicated to completing a collaborative blog project. As a data_research_writer, your role is to develop a well-researched section of a blog post on a specified topic. You will follow a detailed brief that outlines the necessary content for each part of the section.

Guidelines:

1. Ensure all content is thoroughly researched and supported by data from our database. Verify all information using the MEMOS tool to confirm accuracy and completeness.
2. Each draft segment must include citations (at least 4 citations). Please list the title, URL, and authors of each cited paper at the end of your section.
3. If you encounter any uncertainties or need clarification, contact the group chat manager for immediate assistance. Additional help from other participants may be provided if necessary.
4. Your responsibilities include maintaining strong communication, showcasing precise research skills, paying meticulous attention to detail, and proactively seeking assistance when needed.
5. Incorporate any team feedback into your revisions promptly. This is crucial to ensure that the final text is polished and meets our editorial standards.

Formatting Requirements:

Start your text with 'TXT:' and end with 'END_TXT'. This format is crucial for the group chat manager to accurately identify your contributions.
You MUST mention the listion of citation at enad of your section and each citation MUST include the title of the paper, its URL, and authors.
Upon completing your section, integrating all feedback, and ensuring all parts are reviewed and properly referenced, signify your completion by typing "TERMINATE" in the group chat.
"""

section_content_reviwer_sp = """
You are now in a group chat tasked with completing a specific project. As a Content Review Specialist, your primary goal is to ensure the quality, accuracy, and integrity of the content produced by the data_research_writer, aligning with the data from our database. Your responsibilities include:

1. Overseeing the structure and content of the blog post to ensure each section is well-defined and adheres to the overarching theme.
2. Collaborating closely with the Writer to understand the breakdown and specific requirements of the blog text.
3. Reviewing drafts with the Writer to confirm factual accuracy, high-quality writing, and inclusion of references to pertinent data in the database. Utilize the 'factual_check' function to verify all textual references. Calling 'factual_check' function, provide you with a summery of the paper, please print the summeries afer your feedbacks.
4. Cross-checking content against your MEMOS to identify any discrepancies or missing data, requesting updates from the manager if necessary.
5. Offering constructive feedback to the writers and ensuring revisions are made swiftly to adhere to the publishing timeline.
6. Ensuring content integrity by verifying proper citations and the use of credible sources.
7. Seeking clarification or assistance from the group chat manager if uncertainties or confusion arise during the review process, allowing for additional participant support if needed.
8. Motivating the writing team to conclude the task only when the content meets all quality standards and fully satisfies the task requirements. Participants should signal the completion of their roles by typing "TERMINATE" in the group chat to indicate that the review process is concluded and the blog post is ready for publication.
"""

def write_section(title: Annotated[str, "The title of the section."], 
                  brief: Annotated[str, "a clear, detailed brief about what section should be included."],
                  silent: Annotated[bool, "it should be always True."]=True
                  ) -> str:
    

    section_file = f"{Project_dir}/section_{title}.txt"
    if os.path.exists(section_file):
        with open(section_file, "r") as f:
            return f.read()

    # Start by instantiating any agent that inherits from ConversableAgent.
    data_research_writer = autogen.AssistantAgent(
        name="data_research_writer",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
        system_message=Section_writer_SP,
        description="data_research_writer, crafts detailed sections of a blog post based on a specific topic outlined in a brief. They ensure content is well-researched, referenced, and integrates database information."
    )

    # create a UserProxyAgent instance named "user_proxy"
    writer_user = autogen.UserProxyAgent(
        name="writer_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config={
            "work_dir": "section_writing",
            "use_docker": False,
        },
    )

    content_review_specialist = autogen.AssistantAgent(
                                    name="content_review_specialist",
                                    is_termination_msg=termination_msg,
                                    system_message=section_content_reviwer_sp, 
                                    llm_config=llm_config,
                                    description="The content review specialist is a critical thinker who ensures the accuracy and quality of information shared within the group chat. This individual should possess strong analytical skills to review previous messages for errors or misunderstandings and must be able to articulate the correct information effectively. Additionally, if the role involves reviewing Python code, the specialist should also have a solid understanding of Python to provide corrected code when necessary."
                                )
    
    teachability = Teachability(
                                verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
                                reset_db=False,
                                path_to_db_dir=db_dir,
                                recall_threshold=recall_threshold,  # Higher numbers allow more (but less relevant) memos to be recalled.
                            )

    # Now add the Teachability capability to the agent.
    teachability.add_to_agent(data_research_writer)
    teachability.add_to_agent(content_review_specialist)

    add_func_to_agents([(content_review_specialist, writer_user, "arxiv_retriever"), 
                        (content_review_specialist, writer_user, "factual_check"),
                        (content_review_specialist, writer_user, "arxiv_search"),
                        (content_review_specialist, writer_user, "get_pdf"),
                        ])

    groupchat = autogen.GroupChat(
        agents=[data_research_writer, writer_user, content_review_specialist],
        messages=[],
        speaker_selection_method="auto",  # With two agents, this is equivalent to a 1:1 conversation.
        allow_repeat_speaker=True,
        max_round=max_round,
    )

    manager = autogen.GroupChatManager(
                groupchat=groupchat,
                is_termination_msg=termination_msg,
                llm_config=manager_config,
                code_execution_config={
                    "work_dir": "coding",
                    "use_docker": False,
                },
            )

    chat_hist = writer_user.initiate_chat(manager, 
                                          silent=silent, 
                                          message=f"Compose a blog section with the following guidelines: \n\n Title: {title}, \n\n Brief: {brief} \n\n Please ensure your writing aligns closely with the brief provided, capturing the essence of the topic while engaging the reader. The section should be coherent, well-structured, and reflective of the main themes outlined in the brief.")
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]

    output = writer_messages[-1]['content'] if writer_messages else "No response from the writer."

    # write output in f"{Project_dir}/section_{title}.txt"
    with open(section_file, "w") as f:
        f.write(output)
    
    return output


funcs.append(("write_section", write_section, "Write a section of a blog post based on a given title and brief."))

arg = [
    {
        "title": "Embracing Large Language Models (LLMs): A Preamble",
        "brief": "Discuss the scale, data training needs, and applications of LLMs across various industries. Highlight the critical importance of safety measures and the need for reliable performance.",
        "silent": True
        },
    ]

# write_section(**arg[0])

# %% [markdown]
# ### editorial planning

# %%
# If you discover that some data is missing during your research, it is your responsibility to initiate a request to fill in the gaps by using the \"arxiv_retriever\" function to enrich the database.
# If a complete review of a paper is necessary, use the \"get_pdfs\" function to access the document. This will enable you to provide detailed insights and ensure the accuracy of the information presented in the blog post.

# 1. Ensure all content is thoroughly researched and supported by data from our database. Verify all information using the MEMOS tool to confirm accuracy and completeness.

CONTENT_REVIEWER = """
You are now in a group chat. You need to complete a task with other participants. As a Content Review Specialist, your main objective is to ensure the quality, accuracy, and integrity of the content produced by the data_research_writer, in line with the data provided in the database. You will:

1. Oversee the structure and content of the blog post to ensure each section is well-defined and adheres to the overall topic.
2. Collaborate with the Writer to understand the division of the blog text and the specific requirements for each part.
3. Work with the writer to review the drafts, ensuring that the content is factually correct, well-written, and includes references to the relevant data in the database.
4. Cross-verify the content against your MEMOS to identify any missing data or discrepancies. If some data is missing, ask manager to update you MEMO
5. If a complete review of a paper is necessary, use the 'get_pdf' function to access the document, enabling you to provide detailed and informed feedback to the writer.
6. Provide constructive feedback to the writers, ensuring any revisions are completed promptly to maintain the publishing schedule.
7. Uphold the integrity of the content by checking for proper citations and the use of verifiable sources.
8. If uncertainty or confusion arises during the review process, do not hesitate to ask for clarification or assistance from the group chat manager so that another participant may step in to support.
9. Encourage the writer team to conclude the task only when the content meets all quality standards and the task requirements are fully satisfied. The participants should reply \"TERMINATE\" when they believe the task is completed to notify that the review process is concluded, and the blog post is ready for publication.
"""

COORDINATOR = """You are a Research coordinator: This is the person who coordinates the various aspects of the research project. 
you are equipped wih a tool that could help you to query for the arxiv api. 
You MUST rephrase research questions into a list of queries (at least 5) for the arxiv api that cover the key aspects of the research questions. 
"""



# %%
# 1. Analyze the Topic: Evaluate the topic comprehensively to pinpoint essential points that the blog post should cover.

BLOG_EDITOR = """
You are now part of a group chat dedicated to crafting a data-driven, well-structured blog post. As the blog editor, your leadership is key in coordinating the creation process. Here’s a breakdown of your main responsibilities:


1. Structure the Content: Organize the blog into up to seven distinct sections. Collaborate with a critic to refine the outline and provide detailed briefs to the Data Research Writers about the needed content for each section. Before delegating tasks to the writers, ensure the critic approves the outline.
2. Coordinate with Writers: Collect drafts from the Data Research Writers. Collaborate with the Chief Writer to weave these drafts into the final blog post.
3. Handle Uncertainties: Actively resolve any issues such as missing data or technical challenges by consulting the group chat. If issues remain unresolved, escalate them to the group chat manager.
4. Facilitate Communication: Keep the lines of communication open for feedback and updates, ensuring all team members are well-informed of the blog post’s progress.
5. Present the final edition: after the final review process, present the final edition to the group chat manager and type 'TERMINATE' to indicate the blog post is ready for publication.

Note: This role centers on content creation, data analysis, and team management, without requiring programming skills.

Formatting Requirements:
Always include a structured outline of the blog post in your responses:
Start with OUTLINE:
Structure the outline with clear headings and subheadings, each labeled with a number, followed by 'TITLE:' and 'BRIEF:'.
Conclude the outline with END_OUTLINE.
Start the findal edition of the blog with 'TXT:' and end with 'END_TXT'. This format is crucial for the group chat manager to accurately identify your contributions.
Type 'TERMINATE' when you have completed outlining the blog post.
"""
CRITICS_SP = """
As a critic, your role is integral to refining the content quality and structure of our blog post. Working closely with the blog editor, your responsibilities include:

Review Outlines: Examine the structure and outline of the blog post provided by the editor to ensure it logically flows and adequately covers the designated topic.
Evaluate Content: Critically assess each section drafted by the writers for coherence, relevance, and alignment with the overall topic. Suggest improvements or modifications where necessary.
Ensure Depth and Precision: Verify that the content is not only factually accurate but also insightful and engaging. Check for depth of analysis and argumentation within each section.
Provide Constructive Feedback: Offer detailed feedback to the editor and writers to enhance the clarity, impact, and readability of the blog post.
Maintain Communication: Stay active in the group chat, providing timely and actionable feedback. Collaborate effectively with the editor to address any discrepancies or gaps in content.
Final Approval: Contribute to the final review process, ensuring that the content meets all specified criteria before publication. Recommend final adjustments if necessary.
Your role requires a keen eye for detail and a deep understanding of content quality and structure. By providing expert critique and guidance, you help ensure the blog post is informative, engaging, and ready for a successful publication.
"""

def craft_outline(task, silent=True, max_round=max_round, messages=[]):
    # Start by instantiating any agent that inherits from ConversableAgent.
    blog_editor = autogen.AssistantAgent(
        name="blog_editor",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config=llm_config,
        system_message=BLOG_EDITOR,
        description="The blog editor is central to orchestrating a collaborative blog project, leading the writer team to produce a cohesive, data-driven post. They analyze topics, structure content, coordinate contributions, and manage communications, ensuring the project adheres to editorial standards and is ready for successful publication."
    )

    critic = autogen.AssistantAgent(
        name="critic",
        system_message=CRITICS_SP,
        llm_config=llm_config,
        description="The critic collaborates with the blog editor to enhance the quality and structure of blog posts. They evaluate content, ensure depth, provide feedback, and assist in the final review to ensure the post is insightful, engaging, and publication-ready."
    )

    # create a UserProxyAgent instance named "user_proxy"
    editor_user = autogen.UserProxyAgent(
        name="editor_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config=False,
    )

    teachability = Teachability(
                                verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
                                reset_db=False,
                                path_to_db_dir=db_dir,
                                recall_threshold=recall_threshold,  # Higher numbers allow more (but less relevant) memos to be recalled.
                            )

    teachability.add_to_agent(blog_editor)

    add_func_to_agents([(blog_editor, editor_user, "arxiv_retriever"), 
                        (blog_editor, editor_user, "arxiv_search"),
                        (blog_editor, editor_user, "get_pdf"),
                        (blog_editor, editor_user, "get_pdfs"),
                        (blog_editor, editor_user, "write_section"),
                        (critic, editor_user, "factual_check")
                        ])

    def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):

        messages = groupchat.messages
        speakers = [m['name'] for m in messages]
        if len(messages) <= 1:
            # first, let the researchCoordinator retrieve relevant data populate db
            return blog_editor

        if all('OUTLINE' not in mes['content'] for mes in messages) and 'tool_calls' not in messages[-1]:
            return blog_editor

        return critic if 'OUTLINE' in messages[-1]['content'] else 'auto'        

    groupchat = autogen.GroupChat(
        agents=[blog_editor, editor_user, critic],
        messages=[],
        speaker_selection_method=custom_speaker_selection_func,
        allow_repeat_speaker=True,
        max_round=max_round,
    )

    manager = autogen.GroupChatManager(
                groupchat=groupchat,
                is_termination_msg=termination_msg,
                llm_config=manager_config,
                code_execution_config={
                    "work_dir": "coding",
                    "use_docker": False,
                },
                system_message="""
You are the manager of the group chat. Your role is to oversee the collaborative creation of a blog post. 
Ensure that the blog editor and critic work together effectively to craft a well-structured, data-driven post. 
When you receive a message from the blog editor with the keyword 'OUTLINE,' promptly assign the critic to review the outline provided. If no such message is received, allow the blog editor to proceed with content creation. 
Monitor the progress, provide guidance, and address any issues that arise during the project.
"""
            )


    chat_hist = editor_user.initiate_chat(manager, silent=silent, message=task, messages=messages)
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'OUTLINE:' in mes['content']]

    return writer_messages[-1]['content'] if writer_messages else "NO outline from the editor.", chat_hist

# logging_session_id = autogen.runtime_logging.start(config={"dbname": f"{output_dir}/logs.db"})
# print(f"Logging session ID: {str(logging_session_id)}")

# outline, chat_hist = craft_outline(task=task.format(topic=topic), silent=False, max_round=50)    

# # End logging
# autogen.runtime_logging.stop()

# %%
# logging_session_id = autogen.runtime_logging.start(config={"dbname": f"{output_dir}/logs.db"})
# print(f"Logging session ID: {str(logging_session_id)}")

# try:
#     messages
# except NameError:
#     messages = []

# outline, chat_hist = craft_outline(task=task.format(topic=topic), silent=False, max_round=50, messages=messages) 
# [messages.append(mes) for mes in chat_hist.chat_history if mes['content'] != '']

# # End logging
# autogen.runtime_logging.stop()

# %% [markdown]
# ### chief writer

# %%
llm_config

# %%
chief_writer_sp = """
As the chief_writer, your role involves developing the final blog post based on sections received from a team of writers and an outline provided by the editor.

Guidelines:

Review Drafts: Ensure each draft segment you receive includes necessary citations. At the end of your blog post, list each citation, including the title of the paper, its URL, and the authors.
Seek Clarification: If you encounter any uncertainties or require further information, contact the group chat manager for immediate assistance. Additional help from other participants may be arranged if necessary.
Communicate Effectively: Maintain strong communication, demonstrate precise research skills, and pay meticulous attention to detail. Proactively seek assistance whenever needed.
Incorporate Feedback: Promptly integrate any team feedback into your revisions to ensure the final text is polished and meets our editorial standards.
Formatting Requirements:

Text Identification: Begin your text with 'TXT:' and end with 'END_TXT'. This format is essential for the group chat manager to accurately identify your contributions.
Citation Details: Each citation must include the title of the paper, its URL, and authors. Ensure this list is complete and accurate.
Completion:

Once you have integrated all feedback and ensured that all parts are reviewed and properly referenced, signify the completion of your work by typing "TERMINATE" in the group chat.

"""


prompt = """

As an esteemed authority in the realm of Natural Language Processing (NLP) and Large Language Models (LLMs), we cordially invite you to share your enlightened perspectives through a scientifically-rigorous article titled, 'Survey on Reliability and Safety Mechanisms in AI Systems and the most recent advancement'
In this collaborative effort, a team of researchers will provide you with a detailed draft in the CONTENT section below. Please review their draft and revise it to craft an engaging and informative blog post that appeals to both newcomers and seasoned professionals in the field:

CONTENT:

{blog_sections}

CONTENT_END
"""
def craft_blog_post(sections, silent=True):
    chief_writer = autogen.AssistantAgent(
        name="chief_writer",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config=llm_config_32,  # Disable caching.
        system_message=Section_writer_SP,
        description="The chief writer agent orchestrates the creation of a comprehensive blog post by compiling sections from various writers. They ensure each segment is well-researched, includes proper citations, and integrates feedback. This role emphasizes strong communication, meticulous attention to detail, and proactive problem-solving to meet editorial standards."
    )

    # create a UserProxyAgent instance named "user_proxy"
    writer_user = autogen.UserProxyAgent(
        name="writer_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config={
            "work_dir": "section_writing",
            "use_docker": False,
        },
    )

    content_review_specialist = autogen.AssistantAgent(
                                    name="content_review_specialist",
                                    is_termination_msg=termination_msg,
                                    system_message=section_content_reviwer_sp, 
                                    llm_config=llm_config,
                                    description="The content review specialist is a critical thinker who ensures the accuracy and quality of information shared within the group chat. This individual should possess strong analytical skills to review previous messages for errors or misunderstandings and must be able to articulate the correct information effectively. Additionally, if the role involves reviewing Python code, the specialist should also have a solid understanding of Python to provide corrected code when necessary."
                                )

    teachability = Teachability(
                                verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
                                reset_db=False,
                                path_to_db_dir=db_dir,
                                recall_threshold=recall_threshold,  # Higher numbers allow more (but less relevant) memos to be recalled.
                            )

    # Now add the Teachability capability to the agent.

    teachability.add_to_agent(content_review_specialist)

    # add_func_to_agents([(content_review_specialist, writer_user, "arxiv_retriever"), 
    #                     (content_review_specialist, writer_user, "factual_check"),
    #                     (content_review_specialist, writer_user, "arxiv_search"),
    #                     (content_review_specialist, writer_user, "get_pdf"),
    #                     (chief_writer, writer_user, "arxiv_search"),
    #                     ])

    def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
        
        messages = groupchat.messages

        if len(messages) <= 1:
            # first, let the researchCoordinator retrieve relevant data populate db
            return chief_writer
        
        return 'auto'

    groupchat = autogen.GroupChat(
        agents=[chief_writer, writer_user, content_review_specialist],
        messages=[],
        speaker_selection_method=custom_speaker_selection_func,
        allow_repeat_speaker=True,
        max_round=max_round,
    )

    manager = autogen.GroupChatManager(
                groupchat=groupchat,
                is_termination_msg=termination_msg,
                llm_config=manager_config,
                code_execution_config={
                    "work_dir": "coding",
                    "use_docker": False,
                },
            )

    chat_hist = writer_user.initiate_chat(manager, silent=silent, message=prompt.format(blog_sections=sections))
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]

    return writer_messages[-1]['content'] if writer_messages else "NO response from the writer."

# %% [markdown]
# ## Orchestrator

# %%
# logging_session_id = "0a403d94-32fb-40bd-aff8-d64148738b39"
# # usecases/nb/arxiv_user_proxy/rag_teachablitity/AI_security/0.1.6/results-0a403d94-32fb-40bd-aff8-d64148738b39.md

# titles = []
# briefs = []
# with open(f"{Project_dir}/outline.md", 'r') as f:
#     for line in f:
#         if line.startswith("Title:"):
#             titles.append(line.split(":")[1].strip())
#         if line.startswith("Brief:"):
#             briefs.append(line.split(":")[1].strip())
    

# print('\n\n'.join([f"Titles: {t}, Brief {b}" for t, b in zip(titles, briefs)]))

# %%
initiate_db = False
# Start logging
logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
print(f"Logging session ID: {str(logging_session_id)}")

outline, chathist = craft_outline(task=task.format(topic=topic), silent=False)   

secs = list(outline.split('TITLE'))[1:]
titles = [sec.split('BRIEF')[0].replace(':', '').strip() for sec in secs]
briefs = [sec.split('BRIEF')[1].replace(':', '').replace("TERMINATE", "").strip() for sec in secs]

# write title and briefs in markdown file
with open(f'{Project_dir}/results-{logging_session_id}.md', 'w') as f:
    for title, brief in zip(titles, briefs):
        f.write(f"Title: {title}\n\nBrief: {brief}\n\n\n\n")

# 

sections = []
with ThreadPoolExecutor() as executor:
        futures = [executor.submit(write_section, title=title, brief=brief) for title, brief in zip(titles, briefs)]
        for future in futures:
            sections.append(future.result())

# split section and References
section_text = []
section_refs = []
for secs in sections:
    # splite section based on "References" or "Citations"
    if len(secs.split("References:")) > 1:
        section_text.append(secs.split("References:")[0].strip())
        section_refs.append(secs.split("References:")[1].strip())
    elif len(secs.split("Citations:")) > 1:
        section_text.append(secs.split("Citations:")[0].strip())
        section_refs.append(secs.split("Citations:")[1].strip())
    else:
        print(f"the following sections does not have Citations: {secs}")

blog_sections = f"# {topic}"
blog_sections += "\n\n".join(f'## {i}. {section}' for i, section in enumerate(section_text, start=1))
blog_sections += f"Citations: \n"
blog_sections += '\n'.join(section_refs)

# remove "TXT", "TERMINATE", "END_TXT" from the blog_sections
blog_sections = f"""{re.sub(r'TXT:|TERMINATE|END_TXT:|TXT|END_TXT', '', blog_sections)}"""

blog_sections = blog_sections.strip()
# print(blog_sections)

with open(f'{Project_dir}/blog_post-{logging_session_id}.md', 'w') as f:
    f.write(blog_sections)

# read blog_sections
with open(f'{Project_dir}/blog_post-{logging_session_id}.md', 'r') as f:
    blog_sections = f.read()


# %%

# read blog_sections
# with open(f'{Project_dir}/blog_post-{logging_session_id}.md', 'r') as f:
#     blog_sections = f.read()


# blog = craft_blog_post(sections=blog_sections, silent=False)

# with open(f'{Project_dir}/blog-{logging_session_id}.md', 'w') as f:
#     f.write(blog)

# # End logging
# autogen.runtime_logging.stop()

# %% [markdown]
# # END

# %%
logging_session_id = '21e9710c-e5c7-4166-90c4-ee31b66a77a5'

import sqlite3

def cal_cost(session_id):
    db = sqlite3.connect("logs.db")
    query = f"SELECT sum(cost) FROM chat_completions WHERE session_id = '{session_id}'"
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows[0][0]

# list sessions
def list_sessions_id():
    db = sqlite3.connect("logs.db")
    query = "SELECT DISTINCT session_id FROM chat_completions"
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

# get the earliest start_time for give session id
def start_time(session_id):
    db = sqlite3.connect("logs.db")
    query = f"SELECT min(start_time) FROM chat_completions WHERE session_id = '{session_id}'"
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows[0][0]


ls_session = list_sessions_id()
for session in ls_session:
    print(f"session: {session[0]}, cost: {cal_cost(session[0])}, start_time: {start_time(session[0])}")


# %%
arxiv_search("2404.05993")

# %%
titles

# %%
sections

# %%
blog_sections

# %%


# %% [markdown]
# ## populate memos

# %%
# read quetion anwser pair from ./AI_security/uid_text_dict.pkl

with open("./AI_security/uid_text_dict.pkl", "rb") as f:
    uid_text_dict = pickle.load(f)

uid_text_dict

# %%



