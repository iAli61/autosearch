from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed


class ArxivRetriever(BaseFunction):
    """
    A class representing the arxiv_retriever function.
    """

    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="arxiv_retriever",
            description="Retrieve summaries of papers from arXiv for given query.",
            func=arxiv_retriever,
            project_config=project_config
        )


def initiate_chat_with_paper_info(paper, query, project_config: ProjectConfig):

    db_dir = project_config.db_dir
    project_dir = project_config.project_dir
    config_list = project_config.config_list
    paper_db = project_config.paper_db
    # Create a TeachableAgent and UserProxyAgent to represent the researcher and the user, respectively.
    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user",
                                                       db_dir, config_list, verbosity=0)  # type: ignore
    try:
        arxiver_user.initiate_chat(arxiver,
                                   silent=True,
                                   message=f"The following article is one of the articles that I found for '{query}' topic: \n\n '{paper.title}' by {paper.authors} updated on {paper.updated}: {paper.pdf_url} \nsummary: {paper.summary} \n")

        paper_data = {'url': paper.pdf_url,
                      'local_path': project_dir,
                      'title': paper.title,
                      'authors': ','.join([str(author) for author in paper.authors]),
                      'published_date': paper.published,
                      'last_updated_date': paper.updated,
                      }
        paper_db.add_paper("read_abstracts", paper_data=paper_data)  # Add paper to the database after initiating the chat
        return f"Title: {paper.title} Authors: {paper.authors} URL: {paper.pdf_url} os added to MEMOS\n\n "

    except Exception as e:
        print(f"Error: {e}")


def process_query(query, n_results, project_config: ProjectConfig):
    """Function to process each query and initiate chats for each paper found."""
    paper_db = project_config.paper_db

    papers = ArxivAPI.search(query, n_results=n_results)

    # check if the abstract has been read before
    papers = [paper for paper in papers if not paper_db.check_paper(paper.pdf_url, "read_abstracts")]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_with_paper_info, paper, query, project_config) for paper in papers]
        for future in as_completed(futures):
            future.result()


def arxiv_retriever(
    project_config: ProjectConfig,
    queries: Annotated[List[str], "The list of query texts to search for."],
    n_results: Annotated[int, "The number of results to retrieve for each query."] = 10,
) -> str:

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_query, query_text, n_results, project_config) for query_text in queries]
        for future in as_completed(futures):
            future.result()

    # Instantiate a UserProxyAgent to represent the user. But in this notebook, all user input will be simulated.
    return f"Dear Researcher, Database updated with on the following topics: {', '.join(list(queries))}. Please go ahead with your task."
