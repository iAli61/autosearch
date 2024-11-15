from typing_extensions import Annotated
from autosearch.api.search_manager import SearchManager
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig
from autosearch.data.paper import Paper


class UrlCheck(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="url_check",
            description="Check if the provided URL is from a supported academic source and is for the provided paper's title.",
            func=url_check,
            project_config=project_config
        )


def url_check(
    paper_url: Annotated[str, "The URL of the paper to check."],
    paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
    project_config: ProjectConfig
) -> tuple[bool, str]:
    search_manager = SearchManager(project_config.project_dir)

    # Determine which API to use based on the URL structure
    if 'arxiv.org' in paper_url:
        api_name = 'arxiv'
    elif 'scholar.google.com' in paper_url:
        api_name = 'google_scholar'
    else:
        return False, f"The provided paper URL, {paper_url}, is not from a supported academic source. Please provide a valid URL from arXiv or Google Scholar."

    try:
        paper: Paper = search_manager.get_paper_metadata(paper_url, api_name)
    except Exception as e:
        return False, f"Error retrieving paper metadata: {str(e)}"

    # Process authors
    if isinstance(paper.authors, str):
        paper.authors = [paper.authors]
    elif isinstance(paper.authors, list):
        paper.authors = [str(author) for author in paper.authors]

    if paper.title.lower() != paper_title.lower():
        return False, f"The provided paper URL, {paper_url}, is not for the paper titled '{paper_title}'. Please provide a valid URL for the paper."

    return True, f"The provided paper URL is from {api_name} and is for the paper titled '{paper_title}'. Authors: {', '.join(paper.authors)}"
