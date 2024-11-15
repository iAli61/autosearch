from autosearch.functions.check_reasoning import check_reasoning
from autosearch.functions.text_analysis import chunk_pdf
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig
from autosearch.api.search_manager import SearchManager
from autosearch.data.paper import Paper

from typing_extensions import Annotated
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class GetPDFs(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="get_pdfs",
            description="Retrieve the content of the pdf files from the urls list.",
            func=get_pdfs,
            project_config=project_config
        )


def get_pdfs(
    urls: Annotated[List[str], "The list of URLs of the papers to read."],
    reasons: Annotated[List[str], "The list of reasons for reading the papers. It should be the same size as the urls list."],
    project_config: ProjectConfig,
) -> str:
    paper_db = project_config.paper_db
    initiate_db = project_config.initiate_db
    config_list = project_config.config_list
    search_manager = SearchManager(project_config.project_dir)

    papers_to_process = []
    message = ''

    for url, reason in zip(urls, reasons):
        # Determine which API to use based on the URL structure
        if 'arxiv.org' in url:
            api_name = 'arxiv'
        elif 'scholar.google.com' in url:
            api_name = 'google_scholar'
        else:
            message += f"Unsupported URL: {url}\n"
            continue

        try:
            paper = search_manager.get_paper_metadata(url, api_name)
        except Exception as e:
            message += f"Error retrieving metadata for {url}: {str(e)}\n"
            continue

        if paper_db.check_paper(paper.url, "read_papers"):
            print(f"The article, '{paper.title}', has already been read and shared with you in your memory.")
            message += f"The article, '{paper.title}', has already been read and shared with you in your memory.\n"
            continue
        else:
            if not initiate_db and reason != 'factual_check':
                check_reason = check_reasoning(reason, paper.abstract or paper.summary, config_list)
                if 'no' in check_reason.lower():
                    print(f"The article, '{paper.title}', does not meet the criteria for reading.")
                    message += f"The article, '{paper.title}', does not meet the criteria for reading.\n"
                    continue
            papers_to_process.append((paper, reason))

    def process_paper(paper: Paper, reason: str):
        project_dir = project_config.project_dir
        output_dir = project_dir + "/output"
        try:
            pdf_filename = os.path.basename(paper.url)
            pdf_path = os.path.join(project_dir, 'output', pdf_filename)
            search_manager.download_pdf(paper, output_dir)
            paper.local_path = pdf_path
            chunk_pdf(paper, project_config)
            return f"Successfully processed {paper.title}"
        except Exception as e:
            return f"Error processing {paper.title}: {str(e)}"

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_paper, paper, reason) for paper, reason in papers_to_process]
        for future in as_completed(futures):
            message += future.result() + "\n"

    num_papers = paper_db.count_papers("read_papers")
    print(f"{num_papers} articles have been read, so far.")
    titles = [f"{paper.title} [{paper.url}] updated on {paper.last_updated_date}" for paper, _ in papers_to_process]
    message += f"The articles \n {', and \n'.join(titles)} \n have been read and the content has been shared with you in your memory."
    return message
