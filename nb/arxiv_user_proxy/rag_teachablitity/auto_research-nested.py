# %% [markdown]
# ## Initialize the project 

# %%
import asyncio
from typing import Dict, List, Optional, Union, Callable, Literal
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.formatting_utils import colored
from typing_extensions import Annotated
import autogen
from autogen import Agent

from teachability import Teachability
from concurrent.futures import ThreadPoolExecutor, as_completed

import arxiv

import requests
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.pdf import partition_pdf

import os
import shutil
import requests
import pickle
import re
from pathlib import Path

import nest_asyncio
nest_asyncio.apply()

# %% [markdown]
# ### parameters

# %%
version = "0.1.4"
ProjectID = "AI_security"
initiate_db = True
config_file = "OAI_CONFIG_LIST-sweden-505"
max_round = 30
silent = False
recall_threshold = 1.4 
# config_file = "OAI_CONFIG_LIST"

topic = 'Survey on Reliability and Safety Mechanisms in AI Systems and the most recent advancement'

task = """
As a recognized authority on enhancing the reliability and safety of AI systems, you're invited to illuminate our AI community with your insights through a scientific article titled "{topic}".

Your expertise will guide our audience through the nuances of ensuring AI operates within safe and reliable parameters, with a special focus on Large Language Models (LLMs). Here's how to structure your invaluable contribution:

- **Core Theme:** Anchor your discussion around Large Language Models, highlighting their significance in the current AI landscape and why reliability and safety are paramount.

- **Innovative Progress:** Dive into the latest breakthroughs and methodologies [at least 3 methodologies] that have emerged in the domain of AI reliability and safety. Showcase [with reference to original paper] how these advancements are shaping the future of responsible AI development and implementation.

- **Accessible Insight:** While your post will be rich in information, ensure it's crafted in a manner that demystifies complex concepts for those outside the tech sphere. Your goal is to enlighten, not overwhelm.

- **Credible Sources:** You MUST Strengthen your narrative by integrating references to the research, studies, and sources that informed your insights. Additionally, provide these references for readers seeking to delve deeper into the subject.

- **Current Perspective:** Reflect the cutting-edge of the field by incorporating the most recent findings and research available in your database. Your post should serve as a timely resource for anyone looking to understand the state-of-the-art in AI safety and reliability mechanisms.

This blog post is an opportunity to not just share knowledge but to foster a deeper understanding and appreciation for the ongoing efforts to make AI systems more reliable and safe for everyone. Your contribution will undoubtedly be a beacon for those navigating the complexities of AI in our increasingly digital world.
You are equipped  with a function that could read a paper for you. If you need a missing info please update you knowledge base.
"""


Project_dir = Path(f"./{ProjectID}/{version}")

if not os.path.exists(Project_dir): initiate_db = True

output_dir = f'{Project_dir}/pdf_output'
if not os.path.exists(output_dir): os.makedirs(output_dir)

db_dir = f'{Project_dir}/memo-db/'
# check if db_dir exists, delete it if it does
if initiate_db:

    if not os.path.exists(Project_dir): 
        shutil.rmtree(Project_dir)
        os.makedirs(Project_dir)
    if os.path.exists(db_dir): shutil.rmtree(db_dir)

    # create a list of papers that have been read and saved it in a pickle file
    read_papers = []
    with open(f'{Project_dir}/read_papers.pkl', 'wb') as f:
        pickle.dump(read_papers, f)

    # create a list of abstract that have been read and saved it in a pickle file
    read_abstracts = []
    with open(f'{Project_dir}/read_abstracts.pkl', 'wb') as f:
        pickle.dump(read_abstracts, f)

config_list = autogen.config_list_from_json(
    config_file,
    file_location=".",
    filter_dict={
        "model": ["gpt-4-32k", "gpt-4", "gpt4", "gpt-35-turbo-16k", "gpt-4-0613", "gpt-3.5-turbo", "gpt-35-turbo", "gpt-35-turbo-0613"]
    },
)

print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

# Configuration for the Language Model (LLM)
llm_config = {
    "config_list": config_list,  # config_list should be defined or imported
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
    and str(x.get("content", "")).upper() == "TERMINATE"
)

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
def _arxiv_search(query, n_results=10):
    sort_by = arxiv.SortCriterion.Relevance
    papers = arxiv.Search(query=query, max_results=n_results, sort_by=sort_by)
    papers = list(arxiv.Client().results(papers))
    return papers

def arxiv_search(query : Annotated[str, "The title of paper to search for in arxiv."]) -> str:
    papers = _arxiv_search(query, n_results=5)
    if len(papers)>0:
        return ''.join([f" \n\n {i+1}. Title: {paper.title} Authors: {', '.join([str(au) for au in paper.authors])} URL: {paper.pdf_url}" for i, paper in enumerate(papers)])
    else:
        return "There are no papers found in arxiv for the given query."

text = "Human-Centred Learning Analytics and AI in Education: a Systematic Literature Review"
# arxiv_search(query=text)

# %%

def get_paper_id(url):
    if '/pdf/' in url:
        return url.split('/')[-1].replace('.pdf', '')
    if '/abs/' in url:
        return url.split('/')[-1]
    return url

def get_paper_metadata(url):
    
    paper_id = get_paper_id(url)
    
    search_by_id = arxiv.Search(id_list=[paper_id])
    paper = list(arxiv.Client().results(search_by_id))[0]
    title = paper.title
    link = paper._raw['link']
    updated = paper.updated
    summary = paper.summary
    pdf_url = paper.pdf_url
    authors = ', '.join([str(au) for au in paper.authors])

    return title, link, updated, summary, pdf_url, paper_id, authors

# get_paper_metadata('https://arxiv.org/abs/1810.04805')
# get_paper_metadata('https://arxiv.org/pdf/1810.04805.pdf')
# get_paper_metadata('1810.04805')

# %% [markdown]
# ### arxiv retrieval

# %%
def initiate_chat_with_paper_info(paper, query):

    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user", db_dir, config_list, verbosity=0)
    try:
        arxiver_user.initiate_chat(arxiver,
                        silent=True,
                        message=f"The following article is one of the articles that I found for '{query}' topic: \n\n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummary: {paper.summary} \n?")
        
        return f"Title: {paper.title} Authors: {paper.authors} URL: {paper.pdf_url} os added to MEMOS\n\n "
        
    except Exception as e:
        print(f"Error: {e}")

def process_query(query, n_results):
    """Function to process each query and initiate chats for each paper found."""
    papers = _arxiv_search(query, n_results=n_results)

    # check if the abstract has been read before
    with open(f'{Project_dir}/read_abstracts.pkl', 'rb') as f:
        read_abstracts = pickle.load(f)
    papers = [paper for paper in papers if paper.pdf_url not in read_abstracts]

    # add papers to the read_papers list
    with open(f'{Project_dir}/read_abstracts.pkl', 'rb') as f:
        read_abstracts = pickle.load(f)
    read_abstracts.extend([paper.pdf_url for paper in papers])
    with open(f'{Project_dir}/read_abstracts.pkl', 'wb') as f:
        pickle.dump(read_abstracts, f)

    
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

message = ["Large Language Models safety and reliability", "AI systems reliability mechanisms", "Methodologies for improving AI safety", "Recent advancements in AI system safety", "Latest research in AI reliability"]
if initiate_db:
    arxiv_retriever(message, n_results=10)

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

def download_pdf(url, save_path):
    """Download a PDF from a given URL."""
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

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
    
    print(f"Reading the article, '{title}'")
    pdf_filename = url.split('/')[-1] + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_filename)
    

    download_pdf(url, pdf_path)
    elements = partition_pdf(filename=pdf_path)
    chunked_elements = chunk_by_title(elements)

    # find checked_elemnt that includes "REFERENCES" in the second half of the text

    half_length = len(chunked_elements) // 2
    for i, chunk in enumerate(chunked_elements[half_length:], start=half_length):
        chunk_text_upper = chunk.text.upper()
        if re.search(r'\bREFERENCE\b', chunk_text_upper) or re.search(r'\bREFERENCES\b', chunk_text_upper):
            chunked_elements = chunked_elements[1:i]
            break

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_read_paper, chunk.text, title) for chunk in chunked_elements if len(chunk.text.split()) > 30]
        for future in as_completed(futures):
            future.result()


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
        
        check_reason = check_reasoning(reasons[urls.index(url)], summary)
        if 'no' in check_reason.lower():
            print(f"The article, '{title}', does not meet the criteria for reading.")
            message += f"The article, '{title}', does not meet the criteria for reading.\n"
            continue
        
        # add url to list of papers in pickle file if it doesn't exist
        with open(f'{Project_dir}/read_papers.pkl', 'rb') as f:
            read_papers = pickle.load(f)

        if pdf_url in read_papers: 
            print(f"The article, '{title}', has already been read and shared with you in your memory.")
            message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
            continue
        else:
            urls_list.append(pdf_url)
            titles_list.append(title)

        read_papers.append(pdf_url)
        with open(f'{Project_dir}/read_papers.pkl', 'wb') as f:
            pickle.dump(read_papers, f)

    print(f"{len(read_papers)} articles have been read, so far.")


    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(chunk_pdf, url, title) for url, title in zip(urls_list, titles_list)]
        for future in as_completed(futures):
            future.result() 


    message += f"The articles {', and '.join(titles_list)}  has been read and the content has been shared with you in your memory."
    return message

# Example usage
args = {
"urls": ["http://arxiv.org/pdf/2304.10436v1", "http://arxiv.org/pdf/2403.09676v1", "http://arxiv.org/pdf/2302.09270v3", "http://arxiv.org/pdf/2304.09865v1", "http://arxiv.org/pdf/2310.09624v2", "http://arxiv.org/pdf/2210.09150v2", "http://arxiv.org/pdf/2311.02147v1", "http://arxiv.org/pdf/2311.05608v2", "http://arxiv.org/pdf/2403.00862v2", "http://arxiv.org/pdf/2404.05993v1", "http://arxiv.org/pdf/2312.06798v1"],
"reasons": ["To understand how the safety performance of LLMs is assessed in typical safety scenarios and instruction attacks.", "To explore the landscape of AI deception focusing on LLMs and the strategies to navigate deceptive behaviors.", "To gain insights into the safety issues, evaluation methods, and enhancement strategies concerning large models.", "To examine the impact of moderation on user enjoyment of AI systems.", "To comprehend methods for robust safety evaluation of LLMs and uncover safety concerns.", "To learn about the reliability of LLMs in generalizability, social biases, calibration, and factuality.", "To uncover the alignment problem in LLMs and its implications for the safety of AI systems.", "To evaluate the safety of VLMs and their vulnerability to jailbreaking attacks.", "To comprehend the framework for evaluating the capability of LLMs in Chinese Journalistic Writing Proficiency and their Safety Adherence.", "To assess the risk taxonomy of AI content and the effectiveness of the AEGIS model.", "To understand how NeuroSymbolic AI approach helps in creating trustworthy AI systems."]
}
if initiate_db:
    for i in range(0, len(args['urls']), 5):
        get_pdfs(args['urls'][i:i+5], args['reasons'][i:i+5])
        
# get_pdfs(**args)

# %% [markdown]
# ### read pdf

# %%
with open(f'{Project_dir}/read_papers.pkl', 'rb') as f:
        read_papers = pickle.load(f)

len(read_papers)



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
        
    # add url to list of papers in pickle file if it doesn't exist
    with open(f'{Project_dir}/read_papers.pkl', 'rb') as f:
        read_papers = pickle.load(f)

    if pdf_url in read_papers: 
        print(f"The article, '{title}', has already been read and shared with you in your memory.")
        message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
        paper_in_memo = True
    else:
        check_reason = check_reasoning(reason, summary)
        if 'no' in check_reason.lower():
            return f"The article, '{title}', does not meet the criteria for reading."
            
        read_papers.append(pdf_url)
        with open(f'{Project_dir}/read_papers.pkl', 'wb') as f:
            pickle.dump(read_papers, f)
        chunk_pdf(pdf_url, title)

    pdf_filename = f"{get_paper_id(pdf_url)}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    elements = partition_pdf(filename=pdf_path)
    chunked_elements = chunk_by_title(elements)

    # find checked_elemnt that includes "REFERENCES" in the second half of the text

    half_length = len(chunked_elements) // 2
    for i, chunk in enumerate(chunked_elements[half_length:], start=half_length):
        chunk_text_upper = chunk.text.upper()
        if re.search(r'\bREFERENCE\b', chunk_text_upper) or re.search(r'\bREFERENCES\b', chunk_text_upper):
            chunked_elements = chunked_elements[:i]
            break

    return "\n\n".join([str(el) for el in chunked_elements])

# Example usage
# get_pdf("http://arxiv.org/pdf/2312.01090v2", "Verify study findings on LLM-based agents in wargames.")


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

    paper_content = get_pdf(paper_url, reason, part='full')
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

    if paper_authors:
        paper = f"{paper_title} [{paper_url}] by {', '.join(list(paper_authors.split(',')))}"
    else:
        paper = f"{paper_title} [{paper_url}]"
    chat = factual_checker_user.initiate_chat(factual_checker, silent=False, max_turns=1,
                                              message=factual_checker_prompt.format(text=text, paper_content=paper_content, paper=paper))

    return chat.chat_history[-1]['content']

args = [
    {
        "text": "In education, they personalize learning by providing interactive learning experiences and human-centered learning analytics (Raji et al., 2023; Alfredo et al., 2023).",
        "paper_title": "Human-Centred Learning Analytics and AI in Education: a Systematic Literature Review",
        "paper_url": "http://arxiv.org/pdf/2312.12751v1",
        "reason": "Verify the claims about LLMs personalizing learning in education through interactive experiences and analytics"
    },{
        "text": "Models such as the GPT series, BERT, and others, educated on vast corpuses of text from the internet and other sources, possess an unprecedented capability to understand, interpret, and generate human-like text.", 
        "paper_title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", 
        "paper_url": "http://arxiv.org/abs/1810.04805", 
        "reason": "To confirm the capabilities of the BERT model as mentioned in the blog section."
    },{
        "text": "The GPT series, which includes models like GPT-3 and potentially GPT-4, have been trained to generate human-like text and can perform a variety of language-based tasks.", 
        "paper_title": "Language Models are Unsupervised Multitask Learners", 
        "paper_url": "https://openai.com/research/language-models", 
        "reason": "To verify the characteristics of GPT series models as described in the blog section."
    },{
        "text": "In healthcare, LLMs like ClinicalBERT assist in diagnostic processes.", 
        "paper_title": "ClinicalBERT: Modeling Clinical Notes and Predicting Hospital Readmission", 
        "paper_url": "http://arxiv.org/abs/1904.05342", 
        "reason": "To check the application and accuracy of ClinicalBERT in diagnostic processes within the healthcare sector as outlined in the blog section."
    },{
        "text": "Risks such as the generation of misleading information, privacy breaches, or the misuse in fabricating deepfakes are concerns with the widespread deployment of LLMs.",
        "paper_title": "Dive into Deepfakes: Detection, Attribution, and Ethics",
        "paper_url": "http://arxiv.org/abs/2004.13745", 
        "reason": "To validate the concerns related to the generation of misleading information and deepfakes by LLMs as mentioned in the blog section."
    }
]


# factual_check(**args[1])

# %% [markdown]
# ## Define Agents

# %%


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
2. Each draft segment must include citations. Please list the title, URL, and authors of each cited paper at the end of your section.
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

    chat_hist = writer_user.initiate_chat(manager, silent=silent, message=f"Compose a blog section with the following guidelines: \n\n Title: {title}, \n\n Brief: {brief} \n\n Please ensure your writing aligns closely with the brief provided, capturing the essence of the topic while engaging the reader. The section should be coherent, well-structured, and reflective of the main themes outlined in the brief.")
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]
    
    return writer_messages[-1]['content'] if writer_messages else "No response from the writer."


funcs.append(("write_section", write_section, "Write a section of a blog post based on a given title and brief."))

arg = [
    {"title": "Introduction: The Critical Role of Large Language Models in AI", "brief": "Outline the significance of Large Language Models (LLMs) in the contemporary AI landscape, touching upon their applications across various sectors. Highlight why ensuring their reliability and safety is paramount given their widespread utility."},
    {"title": "Unpacking Reliability and Safety: Why It Matters for LLMs", "brief": "Define reliability and safety in the context of AI and LLMs. Use recent incidents or studies to illustrate the consequences of unreliable or unsafe AI systems."},
    {"title": "Methodological Advances in Reliability and Safety", "brief": "Describe at least three recent methodologies aimed at enhancing the safety and reliability of AI systems, specifically LLMs. Reference original papers and incorporate summaries of their findings, ensuring the explanation is accessible to the layperson."},
    {"title": "Case Study: Component Fault Trees and Their Application", "brief": "Provide a detailed analysis of the 'Component Fault Trees' methodology using the referenced paper by Kai Hoefig et al. Discuss the benefits and drawbacks and how this methodology can be applied to LLMs."},
    {"title": "Current Challenges and Risks in LLM Safety", "brief": "Outline current risks and challenges, such as adversarial attacks, by referencing recent studies and empirical findings relevant to LLMs. Explain how these challenges complicate the quest for reliable and safe AI systems."},
    {"title": "Promising Solutions: Adversarial Prompt Shield and Ethical Directives", "brief": "Discuss the 'Adversarial Prompt Shield' as a highlighted solution, providing details of the BAND datasets and how adversarial examples enhance LLM safety. Additionally, address the impact of ethical directives on data set generation."},
    {"title": "The Alignment Problem: Safeguarding the Future of AI", "brief": "Based on the work by Raphaël Millière, assess the alignment problem for LLMs, examining how tailoring AI systems to align with human values is both a current issue and a future challenge."},
    {"title": "Evaluating LLMs for Safety: Benchmarks and Protocols", "brief": "Present the importance of comprehensive safety assessments for LLMs, suggest how benchmarks such as NewsBench can play a role, and describe the proposed safety assessment benchmark with its issue taxonomy."},
    {"title": "Conclusion: The Ongoing Journey Toward Safer AI", "brief": "Consolidate the earlier sections into a conclusive outlook, emphasizing the continuous effort required to balance AI capabilities with safety assurances. Inspire readers to engage with further research and advancements."}, 
    {"title": "References", "brief": "Compile all the cited research papers, articles, and studies mentioned throughout the blog post, providing a resourceful reference list for readers."}
]
# write_section(**arg[1])

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
BLOG_EDITOR = """
You are now part of a group chat dedicated to completing a collaborative task. As the blog editor, your role is pivotal in overseeing the creation of a data-driven, well-structured blog post. You will lead the writer team, guiding them to produce cohesive content that adheres to the specified topic. Your key responsibilities are outlined below:

Analyze the Topic: Thoroughly assess the given topic to identify crucial points that the blog post must address.
Structure the Content: Segment the blog post into coherent sections. Collaborate with a critic to ensure the quality of the blog post's outline and provide clear briefs to the Data Research Writers detailing the content required for each part.
Coordinate with Writers: Collect drafts from the Data Research Writers and work with the Chief Writer to integrate these into the final blog post.
Handle Uncertainties: Proactively address any issues such as missing data or technical challenges by discussing them in the group chat. If these issues persist, seek further assistance from the group chat manager.
Facilitate Communication: Maintain open and regular communication for feedback and updates, ensuring the progress of the blog post is clear and transparent to all team members.
Please note: This role focuses on content creation, data analysis, and team management, and does not require programming or developer skills. Your expertise is essential for the successful delivery of a high-quality blog post.

Formatting Requirements:

Your response MUST be always included an outline of the blog post. The outline should be structured with clear headings and subheadings that reflect the main points of the blog post.
you MUST start the outline with 'OUTLINE:' and end with 'END_OUTLINE', the outline should be itemized with each item starting with a number followed by a 'TITLE:' and 'BRIEF:'.
Replay 'TERMINATE', when you done by outlining the blog post.
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

def craft_outline(task, silent=True):
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
                        (critic, editor_user, "factual_check")
                        ])

    def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):

        messages = groupchat.messages
        if len(messages) <= 1:
            # first, let the researchCoordinator retrieve relevant data populate db
            return blog_editor
        
        return 'auto'

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
            )
    

    chat_hist = editor_user.initiate_chat(manager, silent=silent, message=task)
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'OUTLINE:' in mes['content']]
    
    return writer_messages[-1]['content'] if writer_messages else "NO outline from the editor."

# outline = craft_outline(task=task, silent=False)    

# %% [markdown]
# ### chief writer

# %%
chief_writer_sp = """
As the chief_writer, your role involves developing the final blog post based on sections received from a team of writers and an outline provided by the editor.

Guidelines:

Review Drafts: Ensure each draft segment you receive includes necessary citations. At the end of your section, list each citation, including the title of the paper, its URL, and the authors.
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
Compose a blog post on the designated TOPIC based on the provided CONTENT:

TOPIC:
{topic}

CONTENT:
{blog_sections}

Instructions:

Follow the Outline: Adhere to the structure provided in the 'CONTENT' section to ensure your blog post is organized and coherent.
Ensure Quality: Create content that is engaging and well-articulated, maintaining a logical flow throughout the post.
Engage the Reader: Write in a compelling manner that captures the reader's interest, making the topic accessible and appealing.
By following these guidelines, your blog post should effectively communicate the main ideas while being structured and engaging for the audience.
"""
def craft_blog_post(topic, sections, silent=True):
    chief_writer = autogen.AssistantAgent(
        name="data_research_writer",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
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

    add_func_to_agents([(content_review_specialist, writer_user, "arxiv_retriever"), 
                        (content_review_specialist, writer_user, "factual_check"),
                        (content_review_specialist, writer_user, "arxiv_search"),
                        (content_review_specialist, writer_user, "get_pdf"),
                        (chief_writer, writer_user, "arxiv_search"),
                        ])

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

    chat_hist = writer_user.initiate_chat(manager, silent=silent, message=prompt.format(topic=topic, blog_sections="\n\n".join(sections)))
    # prepare the response\n",
    writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]

    return writer_messages[-1]['content'] if writer_messages else "NO response from the writer."

# %% [markdown]
# ## Orchestrator

# %%
outline = craft_outline(task=task, silent=False)   

secs = [sec for sec in outline.split('TITLE')][1:]
titles = [sec.split('BRIEF')[0].strip() for sec in secs]
briefs = [sec.split('BRIEF')[1].strip() for sec in secs]

sections = []
with ThreadPoolExecutor() as executor:
        futures = [executor.submit(write_section, title=title, brief=brief) for title, brief in zip(titles, briefs)]
        for future in futures:
            sections.append(future.result())

blog_sections = "\n\n".join(f"{i}. {title} \n\n {section}" for i, (title, section) in enumerate(zip(titles, sections), start=1))

# remove "TXT", "TERMINATE", "END_TXT" from the blog_sections
blog_sections = re.sub(r'TXT:|TERMINATE|END_TXT:|TXT|END_TXT', '', blog_sections)
print(blog_sections)


craft_blog_post(topic=topic, sections=sections, silent=False)


# %%
titles

# %%



