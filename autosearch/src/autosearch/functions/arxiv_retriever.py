from autosearch.api.arxiv_api import _arxiv_search
from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from typing_extensions import Annotated
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

# the following functions are developed under the assumption that the following variables are defined in the global scope:
# Project_dir: str = "path/to/project"
# PaperDB: PaperDatabase = PaperDatabase("path/to/db")


def initiate_chat_with_paper_info(paper, query):

    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user",
                                                       db_dir, config_list, verbosity=0) # type: ignore
    try:
        arxiver_user.initiate_chat(arxiver,
                        silent=True,
                        message=f"The following article is one of the articles that I found for '{query}' topic: \n\n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummary: {paper.summary} \n")
        
        PaperDB.add_paper(paper.pdf_url, "read_abstracts", paper_data={'local_path':Project_dir})  # Add paper to the database after initiating the chat
        return f"Title: {paper.title} Authors: {paper.authors} URL: {paper.pdf_url} os added to MEMOS\n\n "
        
    except Exception as e:
        print(f"Error: {e}")

def process_query(query, n_results):
    """Function to process each query and initiate chats for each paper found."""
    papers = _arxiv_search(query, n_results=n_results)

    # check if the abstract has been read before
    papers = [paper for paper in papers if not PaperDB.check_paper(paper.pdf_url, "read_abstracts")]

    
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