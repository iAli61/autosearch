
"""
document_analyzer.py: This module provides a class for analyzing PDF documents using Azure's Document Intelligence service.
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.exceptions import HttpResponseError
import os
import json
from typing import List, Dict, Any, Tuple
from langchain.schema import Document
import tiktoken

from autosearch.analysis import tablehelper as tb

from autosearch.api.search_manager import SearchManager


class DocumentAnalyzer:
    """
    A class for analyzing PDF documents using Azure's Document Intelligence service.

    This class provides methods for analyzing PDFs and creating structured documents from the analyzed data.
    """

    def __init__(self, api_key: str, endpoint: str, project_dir: str):
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
        self.search_manager = SearchManager()

    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze a PDF document.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            Dict[str, Any]: The analyzed data from the PDF.

        Raises:
            FileNotFoundError: If the specified PDF file does not exist.
            HttpResponseError: If there's an error in the Azure service request.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")

        try:
            with open(pdf_path, "rb") as f:
                poller = self.client.begin_analyze_document("prebuilt-document", document=f)

            result = poller.result()
            return result.to_dict()
        except HttpResponseError as e:
            print(f"An error occurred: {e}")
            raise

    def create_docs(self, data: Dict[str, Any], max_token_size: int, source_name: str) -> Tuple[List[Document], Dict[str, str], str]:
        """
        Creates documents from input data, separating content based on section headings and page numbers.

        Args:
            data (Dict[str, Any]): Input data containing paragraphs and tables.
            max_token_size (int): Maximum token size for each document.
            source_name (str): Name of the source.

        Returns:
            Tuple[List[Document], Dict[str, str], str]: A tuple containing:
                - List[Document]: Documents created from the input data.
                - Dict[str, str]: Page content extracted from the input data.
                - str: Full markdown text generated from the input data.
        """
        docs = []
        page_content = {str(i): "" for i in range(1, len(data['pages']) + 1)}
        full_md_text = ""
        largest_doc = 0

        table_spans = self._collect_table_spans(data['tables'])
        paragraphs = self._process_paragraphs(data['paragraphs'], table_spans, data['tables'])

        current_section = ""
        current_text = ""
        current_pages = []

        for para in paragraphs:
            if para['type'] == 'section_heading':
                if current_section:
                    docs, full_md_text, largest_doc = self._add_document(
                        docs, current_text, current_pages, source_name, max_token_size, full_md_text, largest_doc
                    )
                current_section = para['content']
                current_text = f"## {current_section}\n\n"
                current_pages = []
            else:
                current_text += para['content']
                current_pages.append(para['page'])

            page_key = str(para['page'])
            page_content[page_key] += para['content']

        # Add the last document
        if current_section:
            docs, full_md_text, largest_doc = self._add_document(
                docs, current_text, current_pages, source_name, max_token_size, full_md_text, largest_doc
            )

        print(f"Created {len(docs)} docs with a total of {self.count_tokens(full_md_text)} tokens. Largest doc has {largest_doc} tokens.")
        return docs, page_content, full_md_text

    def _collect_table_spans(self, tables: List[Dict[str, Any]]) -> Dict[str, int]:
        """Collect spans from tables."""
        spans = {}
        for idx, tab in enumerate(tables):
            if len(tab['spans']) == 1:
                key = str(tab['spans'][0]['offset'])
            else:
                key = str(min(sp['offset'] for sp in tab['spans']))
            spans[key] = idx
        return spans

    def _process_paragraphs(self, paragraphs: List[Dict[str, Any]], table_spans: Dict[str, int], tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process paragraphs and insert tables where necessary."""
        processed = []
        end_of_table = 0
        for para in paragraphs:
            if para['spans'][0]['offset'] >= end_of_table:
                if para.get('role') == 'sectionHeading':
                    processed.append({
                        'type': 'section_heading',
                        'content': para['content'] + "\n\n",
                        'page': para['bounding_regions'][0]['page_number']
                    })
                else:
                    processed.append({
                        'type': 'paragraph',
                        'content': para['content'] + "\n\n",
                        'page': para['bounding_regions'][0]['page_number']
                    })

                # Check for subsequent table
                search_key = str(para['spans'][0]['offset'] + para['spans'][0]['length'] + 1)
                if search_key in table_spans:
                    table_idx = table_spans[search_key]
                    table_content = "\n\n" + tb.tabletomd(tables[table_idx]) + "\n\n"
                    processed.append({
                        'type': 'table',
                        'content': table_content,
                        'page': tables[table_idx]['bounding_regions'][0]['page_number']
                    })
                    end_of_table = self._calculate_end_of_table(tables[table_idx])

        return processed

    def _calculate_end_of_table(self, table: Dict[str, Any]) -> int:
        """Calculate the end offset of a table."""
        if len(table['spans']) > 1:
            return min(sp['offset'] for sp in table['spans']) + sum(sp['length'] for sp in table['spans']) + 1
        else:
            return table['spans'][0]['offset'] + table['spans'][0]['length'] + 1

    def _add_document(self, docs: List[Document], text: str, pages: List[int], source_name: str,
                      max_token_size: int, full_md_text: str, largest_doc: int) -> Tuple[List[Document], str, int]:
        """Add a new document to the list, splitting if necessary."""
        tokens = self.count_tokens(text)
        if tokens <= max_token_size:
            docs.append(Document(page_content=text, metadata={"source": source_name, "pages": pages, "tokens": tokens}))
            full_md_text += text
            largest_doc = max(largest_doc, tokens)
        else:
            # Split the document if it's too large
            parts = self._split_text(text, max_token_size)
            for part in parts:
                part_tokens = self.count_tokens(part)
                docs.append(Document(page_content=part, metadata={"source": source_name, "pages": pages, "tokens": part_tokens}))
                full_md_text += part
                largest_doc = max(largest_doc, part_tokens)
        return docs, full_md_text, largest_doc

    def _split_text(self, text: str, max_token_size: int) -> List[str]:
        """Split text into parts that fit within the max token size."""
        parts = []
        current_part = ""
        for line in text.split('\n'):
            if self.count_tokens(current_part + line + '\n') > max_token_size:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = ""
                if self.count_tokens(line + '\n') > max_token_size:
                    # If a single line is too long, split it
                    words = line.split()
                    for word in words:
                        if self.count_tokens(current_part + word + ' ') > max_token_size:
                            parts.append(current_part.strip())
                            current_part = ""
                        current_part += word + ' '
                else:
                    current_part = line + '\n'
            else:
                current_part += line + '\n'
        if current_part:
            parts.append(current_part.strip())
        return parts

    @staticmethod
    def count_tokens(text: str) -> int:
        """Count the number of tokens in a given text."""
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))

    def save_analysis_result(self, result: Dict[str, Any], output_path: str) -> None:
        """
        Save the analysis result to a JSON file.

        Args:
            result (Dict[str, Any]): The analysis result to save.
            output_path (str): The path where the JSON file should be saved.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def analyze_and_create_docs(self, pdf_path: str, max_token_size: int = 3000
                                ) -> Tuple[List[Document], Dict[str, str], str]:
        """
        Analyze a PDF and create structured documents from it.

        This method combines the analyze_pdf and create_docs steps.

        Args:
            pdf_path (str): The path to the PDF file.
            max_token_size (int): The maximum token size for each created document. Defaults to 3000.

        Returns:
            List[Document]: A list of created documents.
        """
        analysis_result = self.analyze_pdf(pdf_path)
        self.save_analysis_result(analysis_result, f"{self.output_dir}/json/{os.path.basename(pdf_path)}.json")
        return self.create_docs(analysis_result,
                                max_token_size=max_token_size,
                                source_name=os.path.basename(pdf_path))

    def pdf2md_chunck(self, url: str, max_token_size: int = 3000) -> List[Document]:
        """
        Analyze a PDF and create structured documents from it.

        This method combines the analyze_pdf and create_docs steps.

        Args:
            url (str): The url or path to the PDF file.
            max_token_size (int): The maximum token size for each created document. Defaults to 3000.

        Returns:
            List[Document]: A list of created documents.
        """
        if url[-4:] != ".pdf":
            pdf_filename = url.split('/')[-1] + ".pdf"
        else:
            pdf_filename = url.split('/')[-1]

        if url.startswith("http"):
            # Determine which API to use based on the URL structure
            if 'arxiv.org' in url:
                api_name = 'arxiv'
            elif 'scholar.google.com' in url:
                api_name = 'google_scholar'
            else:
                raise ValueError(f"Unsupported URL: {url}")
            
            # Download the PDF
            try:
                pdf_path = self.search_manager.download_pdf(pdf_filename, api_name, self.output_dir)
            except Exception as e:
                print(f"Error downloading PDF: {str(e)}")
                return []
        else:
            pdf_path = url

        docs, pagecontent, fullmdtext = self.analyze_and_create_docs(pdf_path, max_token_size)

        # write fullmdtext to a file
        with open(f"{self.output_dir}/markdown/{pdf_filename}.md", "w") as f:
            f.write(fullmdtext)

        return docs
