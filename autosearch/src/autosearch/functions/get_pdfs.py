from autosearch.functions.check_reasoning import check_reasoning
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.text_analysis import chunk_pdf
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed


class GetPDFs(BaseFunction):
    """
    A class representing the get_pdf function.
    """

    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="get_pdfs",
            description="Retrieve the content of the pdf files from the urls list.",
            func=get_pdfs,
            project_config=project_config
        )


"""
This `get_pdfs` function downloads a list of PDFs from a given URL, extract theirs content, and
partition the content into chunks based on titles, and then initiate a chat to share and memorize
each chunk of the article with a teachable agent and a user.
"""


def get_pdfs(urls: Annotated[List[str], "The list of URLs of the papers to read."],
             reasons: Annotated[List[str], "The list of reasons for reading the papers. it should be same size as urls list."],
             project_config: ProjectConfig,
             ) -> str:

    paper_db = project_config.paper_db
    initiate_db = project_config.initiate_db
    config_list = project_config.config_list

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
        futures = [executor.submit(chunk_pdf, url, metadata, project_config) for url, title in zip(urls_list, metadata_list)]
        for future in as_completed(futures):
            future.result()

    num_papers = paper_db.count_papers("read_papers")
    print(f"{num_papers} articles have been read, so far.")
    titles = [f"{data['title']} [{data['pdf_url']}] updated on {data['updated']}" for data in metadata_list]
    message += f"The articles \n {', and \n'.join(titles)} \n  have been read and the content has been shared with you in your memory."
    return message
