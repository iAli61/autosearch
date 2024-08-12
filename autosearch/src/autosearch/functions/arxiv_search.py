from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated


class ArxivSearch(BaseFunction):
    """
    A class representing the get_pdf function.
    """

    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="arxiv_search",
            description="retrun arxiv pdf_urls from for the given paper title.",
            func=arxiv_search,
            project_config=project_config
        )


def arxiv_search(query: Annotated[str, "The title of paper to search for in arxiv."],
                 ) -> str:
    """
    Search for papers in arXiv based on the given query.

    Args:
        query (str): The title of the paper to search for in arXiv.

    Returns:
        str: A string containing the search results. If papers are found, it returns a formatted string
        with the details of each paper (title, authors, published date, and URL). If no papers are found,
        it returns a message indicating that there are no papers found for the given query.
    """
    papers = ArxivAPI.search(query, n_results=5)
    if len(papers) > 0:
        return ''.join([f" \n\n {i + 1}. Title: {paper.title} Authors: {', '.join([str(au) for au in paper.authors])} Pulished at {paper.published} URL: {paper.pdf_url}" for i, paper in enumerate(papers)])
    else:
        return "There are no papers found in arXiv for the given query."
