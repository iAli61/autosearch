import asyncio
from typing import Dict, List, Optional, Union, Callable
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.formatting_utils import colored
from typing_extensions import Annotated
import autogen

import arxiv

db_dir = './teachability_db'
# check if db_dir exists, delete it if it does
import os
import shutil
if os.path.exists(db_dir): shutil.rmtree(db_dir)

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["gpt-3.5-turbo", "gpt-35-turbo", "gpt-35-turbo-0613", "gpt-4", "gpt4"],
    },
)



print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

def arxiv_retriever(query_text: Annotated[str, "The list of query texts to search for."], 
                    n_results: Annotated[int, "The number of results to retrieve for each query."] = 3,
                    ) -> str:
    
    # Start by instantiating any agent that inherits from ConversableAgent.
    teachable_agent = autogen.ConversableAgent(
        name="teachable_agent",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
    )

    # Instantiate the Teachability capability. Its parameters are all optional.
    teachability = Teachability(
        verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
        reset_db=False,  
        path_to_db_dir=db_dir,
        recall_threshold=1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
    )

    # Now add the Teachability capability to the agent.
    teachability.add_to_agent(teachable_agent)

    # Instantiate a UserProxyAgent to represent the user. But in this notebook, all user input will be simulated.
    user = autogen.UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: "TERMINATE" in x.get("content"),
        max_consecutive_auto_reply=0,
        code_execution_config={"use_docker": False},
    )

    sort_by = arxiv.SortCriterion.Relevance
    papers = arxiv.Search(
        query=query_text,
        max_results=n_results,
        sort_by=sort_by
        )

    for paper in arxiv.Client().results(papers):
        user.initiate_chat(teachable_agent,
                           message=f"The following article is one of the article that I found for '{query_text}' topic: /n/n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummery: {paper.summary} \n?")

    results = list(arxiv.Client().results(papers))
    return "to PI: the database is updated, go ahead and retrieve the topics you are interested in from database. if something is missing, let me know and I will update the database for you."
    # return "Context is:" + '/n'.join([f"{paper.title} by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \n{paper.summary} \n" for paper in results])


message = "Overview of time series forecasting methods"
# retrieve_content(message, n_results=3)

