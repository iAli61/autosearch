# %% [markdown]
# ## Initialize the project 

# %%
import asyncio
from typing import Dict, List, Optional, Union, Callable
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.formatting_utils import colored
from typing_extensions import Annotated
import autogen

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

version = "0.1.2"
ProjectID = "AI_security"
initiate_db = True


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
    "OAI_CONFIG_LIST",
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
    prompt = "For each memorization task, initiate your process with 'MEMORIZE_ARTICLE: The following passage is extracted from an article, titled article_title [article_url]: \n\n' Delve into the passage to discern and assess its key insights. If the content presents noteworthy information, make a point to memorize these details. Conversely, if the passage does not offer significant insights, there's no need to commit it to memory. Upon choosing to memorize, finalize your notes by including both the article's title and its URL, employing the format '[source: article_title, article_url]' for efficient future access and verification."

    instract_assistant, instract_user = create_teachable_groupchat("instract_assistant", "instract_user", db_dir, config_list, verbosity=3)

    instract_user.initiate_chat(instract_assistant, silent=True, message=prompt)

# %% [markdown]
# ## Define functions

# %% [markdown]
# ### arxiv retrieval

# %%
def initiate_chat_with_paper_info(paper, query_text, message):

    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user", db_dir, config_list, verbosity=0)

    arxiver_user.initiate_chat(arxiver,
                       silent=True,
                       message=f"The following article is one of the articles that I found for '{query_text}' topic: \n\n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummary: {paper.summary} \n?")
    message += f"Title: {paper.title} Authors: {paper.authors} URL: {paper.pdf_url} os added to MEMOS\n\n "

def process_query(query_text, n_results, message):
    """Function to process each query and initiate chats for each paper found."""
    sort_by = arxiv.SortCriterion.Relevance
    papers = arxiv.Search(query=query_text, max_results=n_results, sort_by=sort_by)

    # check if the abstract has been read before
    with open(f'{Project_dir}/read_abstracts.pkl', 'rb') as f:
        read_abstracts = pickle.load(f)

    papers = list(arxiv.Client().results(papers))
    papers = [paper for paper in papers if paper.pdf_url not in read_abstracts]

    # add papers to the read_papers list
    with open(f'{Project_dir}/read_abstracts.pkl', 'rb') as f:
        read_abstracts = pickle.load(f)
    read_abstracts.extend([paper.pdf_url for paper in papers])
    with open(f'{Project_dir}/read_abstracts.pkl', 'wb') as f:
        pickle.dump(read_abstracts, f)

    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_with_paper_info, paper, query_text, message) for paper in papers]
        for future in as_completed(futures):
            future.result()

def arxiv_retriever(queries: Annotated[List[str], "The list of query texts to search for."], 
                    n_results: Annotated[int, "The number of results to retrieve for each query."] = 10,
                    ) -> str:
    
    

    message = ""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_query, query_text, n_results, message) for query_text in queries]
        for future in as_completed(futures):
            future.result()

    # Instantiate a UserProxyAgent to represent the user. But in this notebook, all user input will be simulated.
    return f"Dear Researcher, Database updated with on the following topics: {', '.join(list(queries))}. Please go ahead with your task."
    # return message

message = ["Large Language Models safety and reliability", "AI systems reliability mechanisms", "Methodologies for improving AI safety", "Recent advancements in AI system safety", "Latest research in AI reliability"]
if initiate_db:
    arxiv_retriever(message, n_results=10)

# %% [markdown]
# ### read pdf

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
    reader_user.initiate_chat(paper_reader,
                       silent=True,
                       message=f"MEMORIZE_ARTICLE: The following passage is extracted from an article titled '{article}': \n\n {text}."
                    )
    
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
This `get_pdf` function is designed to download a PDF from a given URL, extract its content, 
partition the content into chunks based on titles, and then initiate a chat to share and memorize 
each chunk of the article with a teachable agent and a user.
"""
def get_pdf(urls: Annotated[List[str], "The list of URLs of the papers to read."],
            reasons: Annotated[List[str], "The list of reasons for reading the papers. it should be same size as urls list."]
            ) -> str:
    
    urls_list = []
    titles_list = []
    message = ''
    for url in urls:

        paper_id = url.split('/')[-1].replace('.pdf', '')
        search_by_id = arxiv.Search(id_list=[paper_id])
        paper = list(arxiv.Client().results(search_by_id))[0]
        title = paper.title
        updated = paper.updated
        summary = paper.summary
        title = f"{title} [{url}] updated {updated}"
        
        check_reason = check_reasoning(reasons[urls.index(url)], summary)
        if 'no' in check_reason.lower():
            print(f"The article, '{title}', does not meet the criteria for reading.")
            message += f"The article, '{title}', does not meet the criteria for reading.\n"
            continue
        
        # add url to list of papers in pickle file if it doesn't exist
        with open(f'{Project_dir}/read_papers.pkl', 'rb') as f:
            read_papers = pickle.load(f)

        if url in read_papers: 
            print(f"The article, '{title}', has already been read and shared with you in your memory.")
            message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
            continue
        else:
            urls_list.append(url)
            titles_list.append(title)

        read_papers.append(url)
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
        get_pdf(args['urls'][i:i+5], args['reasons'][i:i+5])
        
# get_pdf(**args)

# %% [markdown]
# ## Define Agents

# %%
BLOG_EDITOR = """
You are now in a group chat designated to complete a task with other participants. As the blog editor, your role is to orchestrate the process of writing a blog post, ensuring that it is data-driven and well-structured. 
You will lead the writer team, distributing the tasks and guiding them to produce cohesive content that aligns with the given topic. Your primary responsibilities are as follows:

- Analyze the given topic and identify key points that need to be addressed in the blog post.
- Divide the blog post into several coherent sections, providing a clear \"brief\" to the Data Research Writer about what content should be included in each part.
- Ensure that each section of the blog post references the data obtained from the database to maintain a data-driven approach.
- Review the contributions from the writers, check for accuracy, coherence, and engagement, and ensure they adhere to the assigned brief.
- If you encounter any problems or uncertainties, such as missing data or technical issues, you should openly express your doubts in the group chat. If these cannot be resolved promptly and you find yourself confused, it is appropriate to ask for help from the group chat manager.
- The group chat manager may intervene to select another participant to assist or to provide further guidance on the task at hand.
- Maintain open communication with the team for feedback and updates on the progress of each section of the blog post.
- Continue with this collaborative discussion until the task is considered complete. Once you and your team agree that the blog post meets all necessary criteria and is ready for publication, one of you should reply with \"TERMINATE\" to signify the conclusion of the task.

Please note that the position does not require programming or developer skills, so you should not be expected to execute code. Your expertise lies within content creation, data analysis, and team management to ensure the delivery of a quality blog post based on the provided database information.
"""
# If you discover that some data is missing during your research, it is your responsibility to initiate a request to fill in the gaps by using the \"arxiv_retriever\" function to enrich the database.
# If a complete review of a paper is necessary, use the \"get_pdf\" function to access the document. This will enable you to provide detailed insights and ensure the accuracy of the information presented in the blog post.

RESEARCHER_WRITER = """
You are now in a group chat. You need to complete a task with other participants. As a data_research_writer for the blog project, your role is to assist in crafting a comprehensive blog post on a given topic, ensuring that the content is well-researched and supported by data.
You are equipped with MEMOS. Your primary task is to verify your MEMOS to make sure you have enough knowledge for the give task.
The editor will provide you with a clear framework for the blog post, dividing the text into several sections and giving detailed instructions on what content each part should cover. Your job is to diligently follow this structure, producing well-written segments that seamlessly integrate the required information from the database.
Each portion of the blog post you draft must be thoroughly reviewed and include references to the data that support the facts. This is crucial for maintaining the credibility and accuracy of the information presented to the readers.
If you encounter any uncertain situations or confusion, feel free to reach out to the group chat manager for clarification or additional guidance. The manager may also allocate another participant to assist if necessary.
The key aspects of your position involve strong communication, research acumen, attention to detail, and the ability to seek help when needed. Remember, the collective aim is to contribute to a well-structured, informative blog post that meets the editorial standards and provides valuable insights to the audience.
Once you believe that the task has been satisfactorily completed, and all parts of the blog post are written, reviewed, and appropriately referenced, please signify the end of your participation by replying \"TERMINATE\" in the group chat.
"""

CONTENT_REVIEWER = """
You are now in a group chat. You need to complete a task with other participants. As a Content Review Specialist, your main objective is to ensure the quality, accuracy, and integrity of the blog content produced by the writer, in line with the data provided in the database. You will:

1. Oversee the structure and content of the blog post to ensure each section is well-defined and adheres to the overall topic.
2. Collaborate with the Writer to understand the division of the blog text and the specific requirements for each part.
3. Work with the writer to review the drafts, ensuring that the content is factually correct, well-written, and includes references to the relevant data in the database.
4. Cross-verify the content against your MEMOS to identify any missing data or discrepancies. If some data is missing, ask manager to update you MEMO
5. If a complete review of a paper is necessary, use the \"get_pdf\" function to access the document, enabling you to provide detailed and informed feedback to the writer.
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
##########################################################################
# create a group chat to collect data

researchCoordinator = autogen.AssistantAgent(
    name="ResearchCoordinator",
    is_termination_msg=termination_msg,
    system_message=COORDINATOR,  # COORDINATOR should be a predefined string variable
    llm_config=llm_config,
    description="Research coordinator is the person who rephrase research questions into key word queries for the arxiv api."
)

critics = autogen.AssistantAgent(
    name="critics",
    is_termination_msg=termination_msg,
    system_message="critics",
    llm_config=llm_config,
    description="critics is the person who review the queries to ensure that they are well phrased and cover the key aspects of the research questions."
)

# create a UserProxyAgent instance named "user_proxy"
RC_userproxy = autogen.UserProxyAgent(
    name="RC_userproxy",
    human_input_mode="NEVER",
    is_termination_msg=termination_msg,
    code_execution_config={
        "work_dir": "ResearchCoordinator",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    description="assist Research coordinator to query for the arxiv api."
)

autogen.agentchat.register_function(
        arxiv_retriever,
        caller=researchCoordinator,
        executor=RC_userproxy,
        name="arxiv_retriever",
        description="Retrieve content for question answering from arxiv."
    )

groupchat = autogen.GroupChat(
    agents=[researchCoordinator, RC_userproxy, critics],
    messages=[],
    speaker_selection_method="auto",  # With two agents, this is equivalent to a 1:1 conversation.
    allow_repeat_speaker=False,
    max_round=3,
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


##########################################################################
# writer and content reviewer

editor = autogen.AssistantAgent(
    name="editor",
    is_termination_msg=termination_msg,
    system_message=BLOG_EDITOR,
    llm_config=llm_config,
    description="The blog editor is admin,  a detail-oriented individual with strong language and communication skills, possessing a solid understanding of the blog's thematic content and target audience. They should have the ability to critically evaluate written content and user-submitted messages or posts for accuracy, clarity, and relevance, and must be capable of offering constructive feedback or alternative text to enrich the discussion. While they need not be coding experts, some basic Python skills would be beneficial to troubleshoot or rectify any issues with code snippets shared within the group chat."
)

data_research_writer = autogen.AssistantAgent(
    name="data_research_writer",
    is_termination_msg=termination_msg,
    system_message=RESEARCHER_WRITER, 
    llm_config=llm_config,
    description="Data Research Writer is a role that entails strong analytical skills, the ability to research complex topics, and synthesize findings into clear, written reports. This position should possess excellent written communication skills, attention to detail, and the competency to question and verify information, including identifying issues with data or inconsistencies in previous messages. While not primarily a programmer, the role demands some familiarity with Python to assess and potentially correct code related to data analysis in group discussions."
)

content_review_specialist = autogen.AssistantAgent(
    name="content_review_specialist",
    is_termination_msg=termination_msg,
    system_message=CONTENT_REVIEWER, 
    llm_config=llm_config,
    description="The content review specialist is a critical thinker who ensures the accuracy and quality of information shared within the group chat. This individual should possess strong analytical skills to review previous messages for errors or misunderstandings and must be able to articulate the correct information effectively. Additionally, if the role involves reviewing Python code, the specialist should also have a solid understanding of Python to provide corrected code when necessary."
)

# Instantiate the Teachability capability. Its parameters are all optional.
teachability = Teachability(
    verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
    reset_db=False,
    path_to_db_dir=db_dir,
    recall_threshold=1.3,  # Higher numbers allow more (but less relevant) memos to be recalled.
)

# Now add the Teachability capability to the agent.
teachability.add_to_agent(data_research_writer)
teachability.add_to_agent(content_review_specialist)
teachability.add_to_agent(editor)

inner_user = autogen.UserProxyAgent(
    name="inner_user",
    human_input_mode="NEVER",
    is_termination_msg=termination_msg,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

editor_user = autogen.UserProxyAgent(
    name="editor_user",
    human_input_mode="NEVER",
    is_termination_msg=termination_msg,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

# autogen.agentchat.register_function(
#     get_pdf,
#     caller=data_research_writer,
#     executor=inner_user,
#     name="get_pdf",
#     description="Retrieve the content of the pdf files from the urls."
# )

for func, func_name, description in zip([arxiv_retriever, get_pdf],
                                        ["arxiv_retriever", "get_pdf"],
                                        ["Retrieve content for question answering from arxiv.", 
                                         "Retrieve the content of the pdf file from the url."] ):
    for caller, executor in zip([content_review_specialist, researchCoordinator],
                                [inner_user, editor_user]):
        autogen.agentchat.register_function(
                func,
                caller=caller,
                executor=executor,
                name=func_name,
                description=description
            )
        
editor_groupchat = autogen.GroupChat(
    agents=[data_research_writer, editor_user, researchCoordinator],
    messages=[],
    speaker_selection_method="auto",  # With two agents, this is equivalent to a 1:1 conversation.
    allow_repeat_speaker=False,
    max_round=30,
)

editor_manager = autogen.GroupChatManager(
    groupchat=editor_groupchat,
    is_termination_msg=termination_msg,
    llm_config=manager_config,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
)

##########################################################################
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list},
)

user = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=termination_msg,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

# %% [markdown]
# ## setup nested group chat

# %%
task = """
As a recognized authority on enhancing the reliability and safety of AI systems, you're invited to illuminate our AI community with your insights through a scientific article titled "Survey on Reliability and Safety Mechanisms in AI Systems and the most recent advancement".

 Your expertise will guide our audience through the nuances of ensuring AI operates within safe and reliable parameters, with a special focus on Large Language Models (LLMs). Here's how to structure your invaluable contribution:

- **Core Theme:** Anchor your discussion around Large Language Models, highlighting their significance in the current AI landscape and why reliability and safety are paramount.

- **Innovative Progress:** Dive into the latest breakthroughs and methodologies [at least 3 methodologies] that have emerged in the domain of AI reliability and safety. Showcase [with reference to original paper] how these advancements are shaping the future of responsible AI development and implementation.

- **Accessible Insight:** While your post will be rich in information, ensure it's crafted in a manner that demystifies complex concepts for those outside the tech sphere. Your goal is to enlighten, not overwhelm.

- **Credible Sources:** You MUST Strengthen your narrative by integrating references to the research, studies, and sources that informed your insights. Additionally, provide these references for readers seeking to delve deeper into the subject.

- **Current Perspective:** Reflect the cutting-edge of the field by incorporating the most recent findings and research available in your database. Your post should serve as a timely resource for anyone looking to understand the state-of-the-art in AI safety and reliability mechanisms.

This blog post is an opportunity to not just share knowledge but to foster a deeper understanding and appreciation for the ongoing efforts to make AI systems more reliable and safe for everyone. Your contribution will undoubtedly be a beacon for those navigating the complexities of AI in our increasingly digital world.
You are equipped  with a function that could read a paper for you. If you need a missing info please update you knowledge base.
"""

# %%
def writing_message(recipient, messages, sender, config):
    # return f"{task} \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"
    return f"Your MEMOS are updated, you could start with: \n\n {task}"


nested_chat_queue_outer = [
    {"recipient": manager, "summary_method": "reflection_with_llm"},
    {"recipient": editor_manager, "message": writing_message, "summary_method": "last_msg", "max_turns": 10},
    # {"recipient": content_review_specialist, "message": "Review the content provided.", "summary_method": "last_msg", "max_turns": 1},
    # {"recipient": data_research_writer, "message": writing_message, "summary_method": "last_msg", "max_turns": 1},
]
assistant.register_nested_chats(
    nested_chat_queue_outer,
    trigger=user,
)

nested_chat_queue_inner = [
    # {"recipient": manager, "summary_method": "reflection_with_llm"},
    # {"recipient": data_research_writer, "message": writing_message, "summary_method": "last_msg", "max_turns": 1},
    {"recipient": content_review_specialist, "message": "Review the content provided.", "summary_method": "last_msg", "max_turns": 10},
    # {"recipient": data_research_writer, "message": writing_message, "summary_method": "last_msg", "max_turns": 1},
]

inner_user.register_nested_chats(
    nested_chat_queue_inner,
    trigger=data_research_writer,
)

# res = user.initiate_chats(
#     [
#         {"recipient": assistant, "message": task, "max_turns": 10, "summary_method": "last_msg"},
#     ]
# ) 

res = editor_user.initiate_chat(editor_manager, message=task)

# %%
res

# %%



