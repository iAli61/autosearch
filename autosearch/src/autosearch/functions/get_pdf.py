from autosearch.functions.text_analysis import momorized_text, chunk_pdf
from autosearch.functions.check_reasoning import check_reasoning
from autosearch.api.arxiv_api import ArxivAPI

from typing_extensions import Annotated
from typing import List, Dict, Any, Literal
import os

# Global configuration object
global_config: Dict[str, Any] = {}


def initialize_get_pdf(
    paper_db,
    doc_analyzer,
    project_dir: str,
    db_dir: str,
    config_list: List[dict],
    initiate_db: bool = False,
    **kwargs
):
    """Initialize the global configuration object."""
    global global_config
    global_config = {
        "paper_db": paper_db,
        "doc_analyzer": doc_analyzer,
        "project_dir": project_dir,
        "db_dir": db_dir,
        "config_list": config_list,
        "initiate_db": initiate_db
    }


PartChoice = Literal['summary', 'full']


def get_pdf_with_config(url: str, reason: str, part: PartChoice, config: Dict[str, Any]) -> str:

    paper_db = config["paper_db"]
    project_dir = config["project_dir"]
    output_dir = project_dir + "/output"
    config_list = config["config_list"]

    metadata = ArxivAPI.get_paper_metadata(url)
    message = ''
    if part == 'summary':
        momorized_text(metadata['summary'], metadata, config)
        return f"Title: {metadata['title']} Authors: {metadata['authors']} URL: {metadata['pdf_url']} \n\n Summary: {metadata['summary']}"

    title = f"{metadata['title']} [{metadata['pdf_url']}] updated on {metadata['updated']}"

    if paper_db.check_paper(metadata["pdf_url"], "read_papers"):
        print(f"The article, '{title}', has already been read and shared with you in your memory.")
        message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
    else:
        if reason != 'factual_check':
            check_reason = check_reasoning(reason, metadata["summary"], config_list)
            if 'no' in check_reason.lower():
                return f"The article, '{title}', does not meet the criteria for reading."

        chunk_pdf(metadata["pdf_url"], metadata, config)

    md_filename = f"{ArxivAPI._extract_arxiv_id(metadata['pdf_url'])}.pdf.md"
    md_path = os.path.join(f"{output_dir}/markdown", md_filename)

    with open(md_path, "r") as f:
        content = f.read()

    return content


def get_pdf(url: Annotated[str, "The URL of the paper to read."],
            reason: Annotated[str, "reason for reading the paper."],
            part: Annotated[PartChoice, "choose do you need entire paper ('full') or a summary is enough."],
            ) -> str:

    global global_config
    if not global_config:
        raise ValueError("Global configuration not initialized. Call initialize_global_config first.")

    return get_pdf_with_config(url, reason, part, global_config)
