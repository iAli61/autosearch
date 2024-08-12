from typing_extensions import Annotated
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig


class UrlCheck(BaseFunction):
    """
    A class representing the get_pdf function.
    """

    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="url_check",
            description="Check if the provided URL is from arxiv.org and is for the provided paper's title.",
            func=url_check,
            project_config=project_config
        )


def url_check(paper_url: Annotated[str, "The URL of the paper to check."],
              paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
              ):
    if paper_url.find('arxiv.org') == -1:
        return False, f"The provided paper URL, {paper_url}, is not from arxiv.org. Please provide a valid arxiv URL."

    metadata = ArxivAPI.get_paper_metadata(paper_url)

    if metadata['title'] != paper_title:
        return False, f"The provided paper URL, {paper_url}, is not for the paper titled '{paper_title}'. Please provide a valid arxiv URL for the paper."

    return True, f"The provided paper URL is from arxiv.org and is for the paper titled '{paper_title}'."
