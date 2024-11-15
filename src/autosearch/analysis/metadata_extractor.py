from autosearch.api.search_manager import SearchManager
from autosearch.data.paper import Paper
from typing import Dict, Any, Optional
import PyPDF2
from fuzzywuzzy import fuzz


class MetadataExtractor:
    def __init__(self, search_manager: SearchManager):
        self.search_manager = search_manager

    def search_for_metadata(self, title: str) -> Optional[Paper]:
        try:
            # Search across all APIs
            results = self.search_manager.search_all(title, n_results=1)

            # Check if we got any results
            for api_results in results.values():
                if api_results:
                    return api_results[0]  # Assuming search_all now returns Paper objects

            return None
        except Exception as e:
            print(f"Error searching metadata for '{title}': {str(e)}")
            return None

    def extract_metadata_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                if metadata is None:
                    return {}
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                    'modification_date': metadata.get('/ModDate', '')
                }
        except Exception as e:
            print(f"Error extracting metadata from PDF {pdf_path}: {str(e)}")
            return {}

    def get_best_metadata(self, title: str, pdf_path: str) -> Paper:
        online_metadata = self.search_for_metadata(title)
        if online_metadata:
            return online_metadata

        pdf_metadata = self.extract_metadata_from_pdf(pdf_path)
        return Paper(
            title=pdf_metadata.get('title', title),
            authors=[pdf_metadata.get('author', 'Unknown')],
            url=pdf_path,
            source='local',
            published_date=pdf_metadata.get('creation_date'),
            last_updated_date=pdf_metadata.get('modification_date')
    )

    def fuzzy_title_match(self, title: str, threshold: int = 90) -> Optional[Paper]:
        results = self.search_manager.search_all(title, n_results=5)
        for api_results in results.values():
            for paper in api_results:
                if fuzz.ratio(title.lower(), paper.title.lower()) >= threshold:
                    return paper
        return None

