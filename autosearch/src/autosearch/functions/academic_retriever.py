from autosearch.project_config import ProjectConfig
from autosearch.api.search_manager import SearchManager
from autosearch.functions.base_function import BaseFunction
from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from typing_extensions import Annotated
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed


class AcademicRetriever(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="academic_retriever",
            description="Retrieve summaries of papers from multiple academic sources for given queries.",
            func=academic_retriever,
            project_config=project_config
        )


def initiate_chat_with_paper_info(paper, query, project_config: ProjectConfig):
    db_dir = project_config.db_dir
    config_list = project_config.config_list
    paper_db = project_config.paper_db

    arxiver, arxiver_user = create_teachable_groupchat("arxiver", "arxiver_user",
                                                       db_dir, config_list, verbosity=0)
    try:
        arxiver_user.initiate_chat(arxiver,
                                   silent=True,
                                   message=f"The following article is one of the articles that I found for '{query}' topic: \n\n '{paper['title']}' by {paper['authors']} URL: {paper.get('pdf_url') or paper.get('url')} \nsummary: {paper.get('summary') or paper.get('abstract')} \n")

        paper_data = {
            'url': paper.get('pdf_url') or paper.get('url'),
            'local_path': project_config.project_dir,
            'title': paper['title'],
            'authors': ",".join(paper['authors']),
            'published_date': paper.get('published') or paper.get('year'),
            'last_updated_date': paper.get('updated') or paper.get('year'),
            'source': paper['source']
        }
        paper_db.add_paper("read_abstracts", paper_data=paper_data)
        return f"Title: {paper['title']} Authors: {paper['authors']} URL: {paper.get('pdf_url') or paper.get('url')} added to MEMOS\n\n "

    except Exception as e:
        print(f"Error: {e}")


def process_query(query, n_results, project_config: ProjectConfig):
    paper_db = project_config.paper_db
    search_manager = SearchManager()

    all_papers = search_manager.search_all(query, n_results=n_results)
    papers = []
    for source_papers in all_papers.values():
        papers.extend(source_papers)

    papers = [paper for paper in papers if not paper_db.check_paper(paper.get('pdf_url') or paper.get('url'), "read_abstracts")]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(initiate_chat_with_paper_info, paper, query, project_config) for paper in papers]
        for future in as_completed(futures):
            future.result()


def academic_retriever(
    project_config: ProjectConfig,
    queries: Annotated[List[str], "The list of query texts to search for."],
    n_results: Annotated[int, "The number of results to retrieve for each query."] = 10,
) -> str:
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_query, query_text, n_results, project_config) for query_text in queries]
        for future in as_completed(futures):
            future.result()

    return f"Dear Researcher, Database updated with on the following topics: {', '.join(list(queries))}. Please go ahead with your task."
