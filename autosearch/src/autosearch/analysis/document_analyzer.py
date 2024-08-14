from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.exceptions import HttpResponseError
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from langchain.schema import Document
import tiktoken
import arxiv
import shutil

from autosearch.analysis import tablehelper as tb
from autosearch.api.search_manager import SearchManager
from typing import Callable
from autosearch.config_types import ProjectConfig
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.data.paper import Paper


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
        self.chunk_pdf_func = chunk_pdf_func

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

    def create_docs(self, data: Dict[str, Any], max_token_size: int, paper: Paper) -> Tuple[List[Document], Dict[str, str], str]:
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

        # Extract title from paragraphs
        title = next((p['content'] for p in data['paragraphs'] if p.get('role') == 'title'), "Untitled Document")

        full_md_text = f"# {title}\n\n"

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
                        docs, current_text, current_pages, paper.source, max_token_size, full_md_text, largest_doc
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
                docs, current_text, current_pages, paper.source, max_token_size, full_md_text, largest_doc
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

    def analyze_and_create_docs(self, pdf_path: str, paper: Paper, max_token_size: int = 3000
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
        return self.create_docs(analysis_result, max_token_size=max_token_size, paper=paper)

    def pdf2md_chunck(self, paper: Paper, max_token_size: int = 3000) -> List[Document]:
        pdf_filename = os.path.basename(paper.url)
        # add .pdf extension if missing
        if not pdf_filename.endswith('.pdf'):
            pdf_filename += '.pdf'
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        if paper.source == 'local':
            # Handle local files
            source_path = paper.local_path if paper.local_path and os.path.exists(paper.local_path) else paper.url
            try:
                shutil.copy2(source_path, pdf_path)
                paper.local_path = pdf_path
            except Exception as e:
                print(f"Error copying local PDF for {paper.title}: {str(e)}")
                raise
        elif paper.url.startswith('http'):
            # Handle remote files
            try:
                # check if the PDF file is already downloaded
                if os.path.exists(pdf_path):
                    print(f"PDF file already exists: {pdf_path}")
                else:
                    self.search_manager.download_pdf(paper, self.output_dir)
            except Exception as e:
                print(f"Error downloading PDF for {paper.title}: {str(e)}")
                raise
        else:
            raise FileNotFoundError(f"PDF file not found: {paper.url, pdf_path, paper.source, paper.local_path}")

        docs, _, fullmdtext = self.analyze_and_create_docs(pdf_path, paper, max_token_size)

        # write fullmdtext to a file
        md_filename = pdf_filename.replace('.pdf', '.md')
        with open(f"{self.output_dir}/markdown/{md_filename}", "w") as f:
            f.write(fullmdtext)

        return docs

    def extract_text_and_title_from_pdf(self, paper: Paper) -> Tuple[str, str]:
        docs = self.pdf2md_chunck(paper)
        md_file = f"{self.output_dir}/markdown/{os.path.basename(paper.url).replace('.pdf', '.md')}"
        with open(md_file, "r") as f:
            full_md_text = f.read()

        # Extract title from the first document chunk
        title = full_md_text.split('\n')[0].replace('# ', '') if docs else paper.title

        return full_md_text, title

    def process_local_pdf(self, paper: Paper, project_config: ProjectConfig) -> Paper:
        try:
            # Extract text and title from PDF using pdf2md_chunck
            pdf_text, pdf_title = self.extract_text_and_title_from_pdf(paper)

            # Try to get metadata by searching for the PDF title
            metadata = self.search_for_metadata(pdf_title)

            if metadata:
                local_path = paper.url
                paper = metadata
                paper.local_path = local_path
                paper.source = 'local'
            else:
                paper.title = pdf_title
                paper.abstract = pdf_text[:500] + "..."  # Use first 500 characters as abstract

            # Chunk the PDF and add to memory using the existing chunk_pdf function
            self.chunk_pdf_func(paper, project_config)

            return paper

        except Exception as e:
            print(f"Error processing {paper.url}: {str(e)}")
            raise Exception(f"Error processing {paper.url}: {str(e)}")

    def search_for_metadata(self, title: str) -> Optional[Paper]:
        try:
            # Search across all APIs
            results = self.search_manager.search_all(title, n_results=1)

            # Check if we got any results
            for api_results in results.values():
                if api_results:
                    return api_results[0]  # Assuming search_all now returns Paper objects

            return None
        except Exception:
            return None

    def _get_arxiv_metadata(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        try:
            file_name = os.path.basename(pdf_path).replace('.pdf', '')
            paper_id = ArxivAPI._extract_arxiv_id(file_name)
            search = arxiv.Search(id_list=[paper_id])
            result = next(arxiv.Client().results(search))
            return {
                'title': result.title,
                'authors': ','.join([author.name for author in result.authors]),
                'published': result.published,
                'updated': result.updated,
                'summary': result.summary
            }
        except Exception:
            return None

    def _create_default_metadata(self, title: str, text: str) -> Dict[str, Any]:
        return {
            'title': title,
            'authors': 'Unknown',
            'published': 'Unknown',
            'updated': 'Unknown',
            'summary': text[:500] + "..."  # Use first 500 characters as summary
        }

    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['title', 'authors', 'published', 'updated', 'summary']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                metadata[field] = 'Unknown'
        return metadata

    def _create_paper_data(self, pdf_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'url': pdf_path,
            'local_path': pdf_path,
            'title': metadata['title'],
            'authors': metadata['authors'],
            'published_date': metadata.get('published', 'Unknown'),
            'last_updated_date': metadata.get('updated', 'Unknown'),
            'source': 'local'
        }
