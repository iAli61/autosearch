from scholarly import scholarly
from .search_api_base import SearchAPIBase
from typing import List, Dict, Any
import os
import requests


class GoogleScholarAPI(SearchAPIBase):
    def search(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        search_query = scholarly.search_pubs(query)
        results = []
        for i in range(n_results):
            try:
                pub = next(search_query)
                bib = pub.get('bib', {})
                results.append({
                    'title': bib.get('title', 'No title available'),
                    'authors': bib.get('author', 'No authors available'),
                    'url': pub.get('pub_url', 'No URL available'),
                    'abstract': bib.get('abstract', 'No abstract available'),
                    'year': bib.get('year', 'No year available')
                })
            except StopIteration:
                break
        return results

    def get_paper_metadata(self, identifier: str) -> Dict[str, Any]:
        pub = next(scholarly.search_pubs(identifier))
        bib = pub.get('bib', {})
        return {
            'title': bib.get('title', 'No title available'),
            'authors': bib.get('author', 'No authors available'),
            'url': pub.get('pub_url', 'No URL available'),
            'abstract': bib.get('abstract', 'No abstract available'),
            'year': bib.get('year', 'No year available')
        }

    def download_pdf(self, identifier: str, output_path: str) -> str:
        pub = next(scholarly.search_pubs(identifier))
        pdf_url = pub.get('eprint_url')

        if not pdf_url:
            raise ValueError(f"No PDF URL found for paper: {identifier}")

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download the PDF
        response = requests.get(pdf_url)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return output_path
