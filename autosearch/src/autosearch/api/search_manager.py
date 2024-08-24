from typing import List, Dict
import os
from .arxiv_api import ArxivAPI
from .google_scholar_api import GoogleScholarAPI
from autosearch.database.paper_database import PaperDatabase
from autosearch.data.paper import Paper


class SearchManager:
    def __init__(self, project_dir):
        self.apis = {
            'arxiv': ArxivAPI(),
            'google_scholar': GoogleScholarAPI(timeout=30),  # Set a 30-second timeout
            # Add more APIs here as they are implemented
        }
        self.project_dir = project_dir
        self.paper_db = PaperDatabase(self.projet_dir)

    def search_all(self, query: str, n_results: int = 10) -> Dict[str, List[Paper]]:
        results = {}
        for api_name, api in self.apis.items():
            try:
                api_results = api.search(query, n_results)
                results[api_name] = api_results
            except Exception as e:
                print(f"Error searching {api_name}: {str(e)}")
                results[api_name] = []
        return results

    def get_paper_metadata(self, identifier: str, api_name: str) -> Paper:
        if api_name not in self.apis:
            raise ValueError(f"Unknown API: {api_name}")
        return self.apis[api_name].get_paper_metadata(identifier)

    def download_pdf(self, paper: Paper, output_dir: str) -> str:
        if paper.source not in self.apis:
            raise ValueError(f"Unknown API: {paper.source}")
        filename = paper.url.split('/')[-1]
        return self.apis[paper.source].download_pdf(paper.url, os.path.join(output_dir, f"{filename}.pdf"))

    def search_and_download(self, query: str, n_results: int = 10, output_dir: str = "./downloads") -> Dict[str, List[Paper]]:
        search_results = self.search_all(query, n_results)
        downloaded_results = {}

        for api_name, results in search_results.items():
            downloaded_results[api_name] = []
            for paper in results:
                try:
                    pdf_path = self.download_pdf(paper, output_dir)
                    paper.local_path = pdf_path
                    downloaded_results[api_name].append(paper)
                except Exception as e:
                    print(f"Error downloading PDF for {paper.title} from {api_name}: {str(e)}")

        return downloaded_results
