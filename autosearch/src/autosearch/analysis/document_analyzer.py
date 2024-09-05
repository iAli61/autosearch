from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from langchain.schema import Document


from autosearch.api.search_manager import SearchManager
from typing import Callable
from autosearch.config_types import ProjectConfig
from autosearch.data.paper import Paper
from autosearch.analysis.azure_document_analyzer import AzureDocumentAnalyzer
from autosearch.analysis.document_processor import DocumentProcessor
from autosearch.analysis.metadata_extractor import MetadataExtractor
from autosearch.analysis.pdf_manager import PDFManager


class DocumentAnalyzer:
    """
    A class for analyzing PDF documents using Azure's Document Intelligence service.

    This class provides methods for analyzing PDFs and creating structured documents from the analyzed data.
    """

    def __init__(self, api_key: str, endpoint: str, project_dir: str, chunk_pdf_func: Callable):
        """
        Initialize the DocumentAnalyzer.

        Args:
            api_key (str): The API key for Azure Document Intelligence.
            endpoint (str): The endpoint URL for Azure Document Intelligence.
        """
        self.client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))
        self.project_dir = project_dir
        self.output_dir = f"{project_dir}/output"
        os.makedirs(f"{self.output_dir}/json", exist_ok=True)
        os.makedirs(f"{self.output_dir}/markdown", exist_ok=True)
        self.search_manager = SearchManager(self.project_dir)
        self.paper_db = self.search_manager.paper_db
        self.azure_analyzer = AzureDocumentAnalyzer(api_key, endpoint)
        self.document_processor = DocumentProcessor()
        self.pdf_manager = PDFManager(project_dir, f"{project_dir}/output")
        self.metadata_extractor = MetadataExtractor(SearchManager(project_dir))
        self.chunk_pdf_func = chunk_pdf_func


    def analyze_and_create_docs(self, pdf_path: str, paper: Paper, max_token_size: int = 3000, reference: bool = False) -> Tuple[List[Document], Dict[str, str], str]:
        
        json_filename =f"{self.pdf_manager.output_dir}/json/{os.path.basename(pdf_path)}.json"
        if os.path.exists(json_filename):
            analysis_result = self.azure_analyzer.load_analysis_result(json_filename)
        else:
            analysis_result = self.azure_analyzer.analyze_pdf(pdf_path)
            self.azure_analyzer.save_analysis_result(analysis_result, json_filename)

        return self.document_processor.create_docs(analysis_result, max_token_size, paper, reference)


    def pdf2md_chunk(self, paper: Paper, max_token_size: int = 3000, reference: bool = False) -> List[Document]:
        pdf_path = self.pdf_manager.ensure_pdf_exists(paper)
        return self.analyze_and_create_docs(pdf_path, paper, max_token_size, reference=reference)[0]

    def process_local_pdf(self, paper: Paper, project_config: ProjectConfig) -> Paper:

        try:
            full_text, extracted_title = self.extract_text_and_title_from_pdf(paper)
            
            # Update the paper's title if we extracted one from the PDF
            if extracted_title != paper.title:
                paper.title = extracted_title

            # Ensure local_path is not None
            if paper.local_path is None:
                raise ValueError("The local path for the paper cannot be None")
            # Search for metadata using the extracted title
            metadata = self.metadata_extractor.get_best_metadata(paper.title, paper.local_path)
            
            if metadata:
                paper = self._update_paper_with_metadata(paper, metadata)
            else:
                # If no metadata found, use the extracted text for the abstract
                paper.abstract = full_text[:500] + "..."  # Use first 500 characters as abstract

            # Chunk the PDF and add to memory using the existing chunk_pdf function
            self.chunk_pdf_func(paper, project_config)

            return paper

        except Exception as e:
            print(f"Error processing {paper.url}: {str(e)}")
            raise

    def extract_text_and_title_from_pdf(self, paper: Paper) -> Tuple[str, str]:
        """
        Extract the full text and title from a PDF file.

        Args:
            paper (Paper): The Paper object containing information about the PDF.

        Returns:
            Tuple[str, str]: A tuple containing the full text and the title of the PDF.

        Raises:
            FileNotFoundError: If the PDF file is not found.
            Exception: For any other errors during processing.
        """
        try:
            # Ensure the PDF exists locally
            pdf_path = self.pdf_manager.ensure_pdf_exists(paper)

            # Check if we've already processed this PDF
            md_filename = os.path.basename(pdf_path).replace('.pdf', '.md')
            md_file_path = os.path.join(self.pdf_manager.output_dir, "markdown", md_filename)

            if os.path.exists(md_file_path):
                # If we've already processed this PDF, read the markdown file
                with open(md_file_path, "r", encoding='utf-8') as f:
                    full_md_text = f.read()
            else:
                # If not, process the PDF
                analysis_result = self.azure_analyzer.analyze_pdf(pdf_path)
                docs, _, full_md_text = self.document_processor.create_docs(
                    analysis_result, 
                    max_token_size=3000,  # You might want to make this configurable
                    paper=paper
                )

                # Save the full markdown text
                with open(md_file_path, "w", encoding='utf-8') as f:
                    f.write(full_md_text)

            # Extract title from the first line of the markdown text
            title_line = full_md_text.split('\n')[0]
            title = title_line.replace('# ', '') if title_line.startswith('# ') else paper.title

            return full_md_text, title

        except FileNotFoundError:
            print(f"PDF file not found: {paper.url}")
            raise

        except Exception as e:
            print(f"Error processing PDF {paper.url}: {str(e)}")
            raise

    def _update_paper_with_metadata(self, original_paper: Paper, metadata_paper: Paper) -> Paper:
        """
        Update the original paper with metadata found from the search.

        Args:
            original_paper (Paper): The original Paper object with local information.
            metadata_paper (Paper): The Paper object with metadata found from the search.

        Returns:
            Paper: An updated Paper object combining local and found metadata.
        """
        updated_paper = Paper(
            title=metadata_paper.title or original_paper.title,
            authors=metadata_paper.authors or original_paper.authors,
            url=original_paper.url,  # Preserve the original URL (local path)
            source='local',  # Keep it as a local source
            pdf_url=metadata_paper.pdf_url,  # Use found PDF URL if available
            local_path=original_paper.local_path,  # Preserve local path
            abstract=metadata_paper.abstract or original_paper.abstract,
            published_date=self._get_best_date(original_paper.published_date, metadata_paper.published_date),
            last_updated_date=self._get_best_date(original_paper.last_updated_date, metadata_paper.last_updated_date),
            summary=metadata_paper.summary or original_paper.summary,
            id=original_paper.id  # Preserve the original ID
        )

        # If the original paper had any additional custom attributes, preserve them
        for attr, value in original_paper.__dict__.items():
            if not hasattr(updated_paper, attr):
                setattr(updated_paper, attr, value)

        return updated_paper

    @staticmethod
    def _get_best_date(original_date: Optional[datetime], metadata_date: Optional[datetime]) -> Optional[datetime]:
        """
        Choose the best date between the original and metadata dates.

        Args:
            original_date (Optional[datetime]): The date from the original paper.
            metadata_date (Optional[datetime]): The date from the metadata.

        Returns:
            Optional[datetime]: The chosen date, preferring the metadata date if available.
        """
        if metadata_date is not None:
            return metadata_date
        return original_date