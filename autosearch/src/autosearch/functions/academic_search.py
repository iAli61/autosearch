from autosearch.project_config import ProjectConfig
from autosearch.api.search_manager import SearchManager
from autosearch.functions.base_function import BaseFunction
from typing_extensions import Annotated


class AcademicSearch(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="academic_search",
            description="Search for papers across multiple academic sources based on the given query.",
            func=academic_search,
            project_config=project_config
        )


def academic_search(
    query: Annotated[str, "The query to search for in academic sources."],
    project_config: ProjectConfig,
) -> str:
    project_dir = project_config.project_dir
    search_manager = SearchManager(project_dir)
    results = search_manager.search_all(query, n_results=5)

    output = ""
    for source, papers in results.items():
        output += f"\nResults from {source}:\n"
        for i, paper in enumerate(papers, 1):
            output += f"\n{i}. Title: {paper.title}\n"
            output += f"   Authors: {', '.join(paper.authors)}\n"
            output += f"   URL: {paper.pdf_url or paper.url}\n"
            if paper.published_date:
                output += f"   Published: {paper.published_date}\n"

    if not output:
        return "No papers found in academic sources for the given query."
    return output
