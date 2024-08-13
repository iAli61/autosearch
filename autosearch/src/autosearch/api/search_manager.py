from typing import List, Dict, Any
from .arxiv_api import ArxivAPI
from .google_scholar_api import GoogleScholarAPI


class SearchManager:
    def __init__(self):
        self.apis = {
            'arxiv': ArxivAPI(),
            'google_scholar': GoogleScholarAPI(),
            # Add more APIs here as they are implemented
        }

    def search_all(self, query: str, n_results: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        for api_name, api in self.apis.items():
            try:
                api_results = api.search(query, n_results)
                for result in api_results:
                    result['source'] = api_name  # Add this line
                results[api_name] = api_results
            except Exception as e:
                print(f"Error searching {api_name}: {str(e)}")
                results[api_name] = []
        return results

    def get_paper_metadata(self, identifier: str, api_name: str) -> Dict[str, Any]:
        if api_name not in self.apis:
            raise ValueError(f"Unknown API: {api_name}")
        return self.apis[api_name].get_paper_metadata(identifier)

    def download_pdf(self, identifier: str, api_name: str, output_path: str) -> str:
        if api_name not in self.apis:
            raise ValueError(f"Unknown API: {api_name}")
        return self.apis[api_name].download_pdf(identifier, output_path)

    def search_and_download(self, query: str, n_results: int = 10, output_dir: str = "./downloads") -> Dict[str, List[Dict[str, Any]]]:
        search_results = self.search_all(query, n_results)
        downloaded_results = {}

        for api_name, results in search_results.items():
            downloaded_results[api_name] = []
            for result in results:
                try:
                    identifier = result['pdf_url'] if 'pdf_url' in result else result['url']
                    output_path = f"{output_dir}/{api_name}_{result['title'][:50]}.pdf"
                    pdf_path = self.download_pdf(identifier, api_name, output_path)
                    result['local_pdf_path'] = pdf_path
                    downloaded_results[api_name].append(result)
                except Exception as e:
                    print(f"Error downloading PDF for {result['title']} from {api_name}: {str(e)}")

        return downloaded_results
