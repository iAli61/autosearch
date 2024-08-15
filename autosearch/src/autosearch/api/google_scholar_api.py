from scholarly import scholarly
from .search_api_base import SearchAPIBase
from autosearch.data.paper import Paper
from typing import List
import os
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class GoogleScholarAPI(SearchAPIBase):
    def __init__(self, timeout=30):
        self.timeout = timeout  # Default timeout of 30 seconds

    def search(self, query: str, n_results: int = 10) -> List[Paper]:
        def search_task():
            search_query = scholarly.search_pubs(query)
            results = []
            for _ in range(n_results):
                try:
                    pub = next(search_query)
                    bib = pub.get('bib', {})
                    authors = bib.get('author', [])
                    if isinstance(authors, str):
                        authors = [authors]
                    elif isinstance(authors, list):
                        authors = [str(author) for author in authors]

                    paper = Paper(
                        title=bib.get('title', 'No title available'),
                        authors=authors,
                        url=pub.get('pub_url', 'No URL available'),
                        abstract=bib.get('abstract', 'No abstract available'),
                        last_updated_date=datetime.strptime(bib.get('year'), "%Y") if bib.get('year') else None,  # type: ignore
                        published_date=datetime.strptime(bib.get('year'), "%Y") if bib.get('year') else None,  # type: ignore
                        source='google_scholar',
                        pdf_url=pub.get('eprint_url')
                    )
                    results.append(paper)
                except StopIteration:
                    break
            return results

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(search_task)
            try:
                return future.result(timeout=self.timeout)
            except TimeoutError:
                print(f"Google Scholar search timed out after {self.timeout} seconds.")
                return []  # Return an empty list if the search times out

    def get_paper_metadata(self, identifier: str) -> Paper:
        pub = next(scholarly.search_pubs(identifier))
        bib = pub.get('bib', {})
        authors = bib.get('author', [])
        if isinstance(authors, str):
            authors = [authors]
        elif isinstance(authors, list):
            authors = [str(author) for author in authors]

        return Paper(
            title=bib.get('title', 'No title available'),
            authors=authors,
            url=pub.get('pub_url', 'No URL available'),
            abstract=bib.get('abstract', 'No abstract available'),
            last_updated_date=datetime.strptime(bib.get('year'), "%Y") if bib.get('year') else None,  # type: ignore
            published_date=datetime.strptime(bib.get('year'), "%Y") if bib.get('year') else None,  # type: ignore
            source='google_scholar',
            pdf_url=pub.get('eprint_url')
        )

    def download_pdf(self, paper: Paper, output_path: str) -> str:
        if not paper.pdf_url:
            raise ValueError(f"No PDF URL found for paper: {paper.title}")

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download the PDF
        response = requests.get(paper.pdf_url)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        # Update the paper's local_path
        paper.local_path = output_path

        return output_path
