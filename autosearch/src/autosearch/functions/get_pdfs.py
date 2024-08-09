# from autosearch.api.arxiv_api import search
from autosearch.functions.check_reasoning import check_reasoning
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.text_analysis import chunk_pdf

from typing_extensions import Annotated
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


# Global configuration object
global_config: Dict[str, Any] = {}


def initialize_get_pdfs(
    paper_db,
    doc_analyzer,
    project_dir: str,
    db_dir: str,
    config_list: List[dict],
    initiate_db: bool = False
):
    """Initialize the global configuration object."""
    global global_config
    global_config = {
        "paper_db": paper_db,
        "doc_analyzer": doc_analyzer,
        "project_dir": project_dir,
        "db_dir": db_dir,
        "config_list": config_list,
        "initiate_db": initiate_db,
        "config_list": config_list
    }


"""
This `get_pdfs` function downloads a list of PDFs from a given URL, extract theirs content, and
partition the content into chunks based on titles, and then initiate a chat to share and memorize
each chunk of the article with a teachable agent and a user.
"""


def get_pdfs(urls: Annotated[List[str], "The list of URLs of the papers to read."],
             reasons: Annotated[List[str], "The list of reasons for reading the papers. it should be same size as urls list."]
             ) -> str:

    global global_config
    if not global_config:
        raise ValueError("Global configuration not initialized. Call initialize_global_config first.")

    paper_db = global_config["paper_db"]
    initiate_db = global_config["initiate_db"]
    config_list = global_config["config_list"]

    urls_list = []
    metadata_list = []
    message = ''
    for url, reason in zip(urls, reasons):

        metadata = ArxivAPI.get_paper_metadata(url)

        title = f"{metadata['title']} [{metadata['pdf_url']}] updated on {metadata['updated']}"

        if paper_db.check_paper(metadata["pdf_url"], "read_papers"):
            print(f"The article, '{title}', has already been read and shared with you in your memory.")
            message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
            continue
        else:
            if not initiate_db and reason != 'factual_check':
                check_reason = check_reasoning(reason, metadata["summary"], config_list)
                if 'no' in check_reason.lower():
                    print(f"The article, '{title}', does not meet the criteria for reading.")
                    message += f"The article, '{title}', does not meet the criteria for reading.\n"
                    continue
            urls_list.append(metadata["pdf_url"])
            metadata_list.append(metadata)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(chunk_pdf, url, metadata, global_config) for url, title in zip(urls_list, metadata_list)]
        for future in as_completed(futures):
            future.result()

    num_papers = paper_db.count_papers("read_papers")
    print(f"{num_papers} articles have been read, so far.")
    titles = [f"{data['title']} [{data['pdf_url']}] updated on {data['updated']}" for data in metadata_list]
    message += f"The articles \n {', and \n'.join(titles)} \n  have been read and the content has been shared with you in your memory."
    return message
