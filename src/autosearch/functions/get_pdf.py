from autosearch.functions.check_reasoning import check_reasoning
from autosearch.functions.text_analysis import chunk_pdf, momorized_text
from autosearch.functions.base_function import BaseFunction
from autosearch.api.search_manager import SearchManager
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated
from typing import Literal
import os


class GetPDF(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="get_pdf",
            description="Retrieve the content of the pdf file from the url.",
            func=get_pdf,
            project_config=project_config
        )


PartChoice = Literal['summary', 'full']


def get_pdf(
    url: Annotated[str, "The URL of the paper to read."],
    reason: Annotated[str, "reason for reading the paper."],
    part: Annotated[PartChoice, "choose do you need entire paper ('full') or a summary is enough."],
    project_config: ProjectConfig,
) -> str:
    paper_db = project_config.paper_db
    project_dir = project_config.project_dir
    output_dir = project_dir + "/output"
    config_list = project_config.config_list

    search_manager = SearchManager(project_dir)

    # Determine which API to use based on the URL structure
    if 'arxiv.org' in url:
        api_name = 'arxiv'
    elif 'scholar.google.com' in url:
        api_name = 'google_scholar'
    else:
        return f"Unsupported URL: {url}"

    try:
        paper = search_manager.get_paper_metadata(url, api_name)
    except Exception as e:
        return f"Error retrieving paper metadata: {str(e)}"

    message = ''
    if part == 'summary':
        # Ensure text is always a string
        text = paper.abstract or paper.summary or "No summary available."
        # Assuming momorized_text function is defined elsewhere and imported
        momorized_text(text, paper, project_config)
        return f"Title: {paper.title} Authors: {', '.join(paper.authors)} URL: {paper.pdf_url or paper.url} \n\n Summary: {paper.abstract or paper.summary}"

    title = f"{paper.title} [{paper.pdf_url or paper.url}] updated on {paper.last_updated_date}"

    if paper_db.check_paper(paper.url, "read_papers"):
        print(f"The article, '{title}', has already been read and shared with you in your memory.")
        message += f"The article, '{title}', has already been read and shared with you in your memory.\n"
    else:
        if reason != 'factual_check':
            check_reason = check_reasoning(reason, paper.abstract or paper.summary, config_list)
            if 'no' in check_reason.lower():
                return f"The article, '{title}', does not meet the criteria for reading."

        try:
            search_manager.download_pdf(paper, output_dir)
            chunk_pdf(paper, project_config)
        except Exception as e:
            return f"Error downloading or processing PDF: {str(e)}"

    md_filename = f"{os.path.basename(paper.pdf_url or paper.url)}.md"
    md_path = os.path.join(f"{output_dir}/markdown", md_filename)

    try:
        with open(md_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return f"Error: Markdown file not found at {md_path}"

    return content
