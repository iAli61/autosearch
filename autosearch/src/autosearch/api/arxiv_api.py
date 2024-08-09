"""
arxiv_api.py: This module provides a class for interacting with the ArXiv API.
"""

import arxiv
import os
import re
from typing import List, Dict
from urllib.parse import urlparse


class ArxivAPI:
    """
    A class for interacting with the ArXiv API.

    This class provides methods for searching papers, retrieving metadata,
    and downloading PDFs from ArXiv.
    """

    @staticmethod
    def search(query: str, n_results: int = 10) -> List[arxiv.Result]:
        """
        Search for papers on ArXiv.

        Args:
            query (str): The search query.
            n_results (int): The number of results to return. Defaults to 10.

        Returns:
            List[arxiv.Result]: A list of search results.
        """
        search = arxiv.Search(
            query=query,
            max_results=n_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        return list(arxiv.Client().results(search))

    @staticmethod
    def get_paper_metadata(identifier: str) -> Dict[str, str]:
        """
        Retrieve metadata for a paper given its ArXiv identifier or URL.

        Args:
            identifier (str): The ArXiv identifier or URL of the paper.

        Returns:
            Dict[str, Union[str, List[str]]]: Metadata of the paper.
        """
        paper_id = ArxivAPI._extract_arxiv_id(identifier)
        search = arxiv.Search(id_list=[paper_id])
        result = next(arxiv.Client().results(search))

        return {
            "title": result.title,
            "authors": ','.join([str(author) for author in result.authors]),
            "summary": result.summary,
            "comment": result.comment,
            "journal_ref": result.journal_ref,
            "doi": result.doi,
            "primary_category": result.primary_category,
            "categories": ','.join(result.categories),
            "links": ','.join([str(link) for link in result.links]),
            "pdf_url": result.pdf_url,
            "published": result.published.isoformat(),
            "updated": result.updated.isoformat(),
        }

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


# Example usage


if __name__ == "__main__":
    # Search for papers
    results = ArxivAPI.search("quantum computing", n_results=5)
    for paper in results:
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(str(author) for author in paper.authors)}")
        print(f"Summary: {paper.summary[:200]}...")
        print(f"PDF URL: {paper.pdf_url}")
        print("---")

    # Get metadata for a specific paper
    paper_url = "https://arxiv.org/abs/2103.11955"
    metadata = ArxivAPI.get_paper_metadata(paper_url)
    print("Paper Metadata:")
    for key, value in metadata.items():
        print(f"{key}: {value}")

    # Download a PDF
    ArxivAPI.download_pdf(paper_url, "example_paper.pdf")
    print("PDF downloaded to: example_paper.pdf")

    # Get full text of a paper
    full_text = ArxivAPI.get_paper_full_text(paper_url)
    print(f"Full text (first 500 characters): {full_text[:500]}...")

    # Batch download PDFs
    identifiers = ["2103.11955", "https://arxiv.org/abs/2103.11956", "2103.11957"]
    results = ArxivAPI.batch_download(identifiers, "downloaded_papers")
    for identifier, result in results.items():
        print(f"Paper {identifier}: {result}")
