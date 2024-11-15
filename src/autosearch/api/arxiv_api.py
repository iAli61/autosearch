import arxiv
from typing import List, Dict
from .search_api_base import SearchAPIBase
import os
import re
from urllib.parse import urlparse
from autosearch.data.paper import Paper


class ArxivAPI(SearchAPIBase):

    def search(self, query: str, n_results: int = 10) -> List[Paper]:
        search = arxiv.Search(
            query=query,
            max_results=n_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for result in search.results():
            results.append({
                'title': result.title,
                'authors': ', '.join(author.name for author in result.authors),
                'summary': result.summary,
                'pdf_url': result.pdf_url,
                'published': result.published.strftime('%Y-%m-%d'),
                'updated': result.updated.strftime('%Y-%m-%d')
            })
        return [Paper(
            title=result.title,
            authors=[author.name for author in result.authors],
            url=result.entry_id,
            pdf_url=result.pdf_url,
            abstract=result.summary,
            published_date=result.published,
            last_updated_date=result.updated,
            source='arxiv'
        ) for result in search.results()]

    def get_paper_metadata(self, identifier: str) -> Paper:
        arxiv_id = self._extract_arxiv_id(identifier)
        paper = next(arxiv.Search(id_list=[arxiv_id]).results())

        return Paper(
            title=paper.title,
            authors=[author.name for author in paper.authors],
            url=paper.entry_id,
            pdf_url=paper.pdf_url,
            abstract=paper.summary,
            published_date=paper.published,
            last_updated_date=paper.updated,
            source='arxiv'
        )

    @staticmethod
    def download_pdf(identifier: str, save_path: str) -> str:
        """
        Download a PDF from ArXiv.

        Args:
            identifier (str): The ArXiv identifier or URL of the paper.
            save_path (str): The path where the PDF should be saved.

        Returns:
            str: The path where the PDF was saved.
        """
        paper_id = ArxivAPI._extract_arxiv_id(identifier)
        search = arxiv.Search(id_list=[paper_id])
        result = next(arxiv.Client().results(search))

        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # chech if save_path has .pdf extention or not
        if not save_path.endswith('.pdf'):
            save_path += '.pdf'

        # Download the PDF
        result.download_pdf(filename=save_path)
        return save_path

    @staticmethod
    def _extract_arxiv_id(identifier: str) -> str:
        """
        Extract the ArXiv ID from a given identifier or URL.

        Args:
            identifier (str): The ArXiv identifier or URL.

        Returns:
            str: The extracted ArXiv ID.

        Raises:
            ValueError: If the input is not a valid ArXiv identifier or URL.
        """
        # Regular expression for ArXiv ID format
        arxiv_id_pattern = r'\d{4}\.\d{4,5}(v\d+)?'

        # Check if it's already a valid ArXiv ID
        if re.fullmatch(arxiv_id_pattern, identifier):
            return identifier

        # If it's a URL, parse it to extract the ID
        parsed_url = urlparse(identifier)
        if 'arxiv.org' in parsed_url.netloc:
            path_parts = parsed_url.path.strip('/').split('/')
            if 'abs' in path_parts or 'pdf' in path_parts:
                potential_id = path_parts[-1].replace('.pdf', '')
                if re.fullmatch(arxiv_id_pattern, potential_id):
                    return potential_id

        raise ValueError(f"Invalid ArXiv identifier or URL: {identifier}")

    @staticmethod
    def get_paper_full_text(identifier: str) -> str:
        """
        Retrieve the full text of a paper given its ArXiv identifier or URL.

        This method downloads the PDF and extracts the text content.

        Args:
            identifier (str): The ArXiv identifier or URL of the paper.

        Returns:
            str: The full text content of the paper.
        """
        import tempfile
        import PyPDF2

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            ArxivAPI.download_pdf(identifier, temp_file.name)

            with open(temp_file.name, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text()

        os.unlink(temp_file.name)
        return full_text

    @staticmethod
    def batch_download(identifiers: List[str], save_dir: str) -> Dict[str, str]:
        """
        Download multiple PDFs from ArXiv in batch.

        Args:
            identifiers (List[str]): A list of ArXiv identifiers or URLs.
            save_dir (str): The directory where PDFs should be saved.

        Returns:
            Dict[str, str]: A dictionary mapping identifiers to their saved file paths.
        """
        os.makedirs(save_dir, exist_ok=True)
        results = {}

        for identifier in identifiers:
            try:
                paper_id = ArxivAPI._extract_arxiv_id(identifier)
                save_path = os.path.join(save_dir, f"{paper_id}.pdf")
                ArxivAPI.download_pdf(identifier, save_path)
                results[identifier] = save_path
            except Exception as e:
                results[identifier] = f"Error: {str(e)}"

        return results
