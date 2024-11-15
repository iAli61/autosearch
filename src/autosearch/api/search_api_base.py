from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SearchAPIBase(ABC):
    @abstractmethod
    def search(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_paper_metadata(self, identifier: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def download_pdf(self, identifier: str, output_path: str) -> str:
        pass