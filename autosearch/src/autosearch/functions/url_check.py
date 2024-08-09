from typing_extensions import Annotated
from autosearch.api.arxiv_api import ArxivAPI


def url_check(paper_url: Annotated[str, "The URL of the paper to check."],
              paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
              ):
    if paper_url.find('arxiv.org') == -1:
        return False, f"The provided paper URL, {paper_url}, is not from arxiv.org. Please provide a valid arxiv URL."

    metadata = ArxivAPI.get_paper_metadata(paper_url)

    if metadata['title'] != paper_title:
        return False, f"The provided paper URL, {paper_url}, is not for the paper titled '{paper_title}'. Please provide a valid arxiv URL for the paper."

    return True, f"The provided paper URL is from arxiv.org and is for the paper titled '{paper_title}'."
