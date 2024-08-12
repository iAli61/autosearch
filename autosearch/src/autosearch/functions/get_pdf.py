from autosearch.functions.check_reasoning import check_reasoning
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.text_analysis import chunk_pdf, momorized_text
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated
from typing import Literal
import os


class GetPDF(BaseFunction):
    """
    A class representing the get_pdf function.
    """

    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="get_pdf",
            description="Retrieve the content of the pdf file from the url.",
            func=get_pdf,
            project_config=project_config
        )


PartChoice = Literal['summary', 'full']


def get_pdf(url: Annotated[str, "The URL of the paper to read."],
            reason: Annotated[str, "reason for reading the paper."],
            part: Annotated[PartChoice, "choose do you need entire paper ('full') or a summary is enough."],
            project_config: ProjectConfig,
            ) -> str:

    paper_db = project_config.paper_db
    project_dir = project_config.project_dir
    output_dir = project_dir + "/output"
    config_list = project_config.config_list

    metadata = ArxivAPI.get_paper_metadata(url)
    message = ''
    if part == 'summary':
        momorized_text(metadata['summary'], metadata, project_config)
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

        chunk_pdf(metadata["pdf_url"], metadata, project_config)

    md_filename = f"{ArxivAPI._extract_arxiv_id(metadata['pdf_url'])}.pdf.md"
    md_path = os.path.join(f"{output_dir}/markdown", md_filename)

    with open(md_path, "r") as f:
        content = f.read()

    return content
