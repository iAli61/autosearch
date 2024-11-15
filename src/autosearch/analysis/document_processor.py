from langchain.schema import Document
import tiktoken
from typing import List, Dict, Any, Tuple
import tiktoken
import numpy as np

from autosearch.analysis import tablehelper as tb
from autosearch.data.paper import Paper

class DocumentProcessor:
    @staticmethod
    def create_docs(data: Dict[str, Any], max_token_size: int, paper: Paper, reference: bool = False) -> Tuple[List[Document], Dict[str, str], str]:
        """
        Creates documents from input data, separating content based on section headings and page numbers.

        Args:
            data (Dict[str, Any]): Input data containing paragraphs and tables.
            max_token_size (int): Maximum token size for each document.
            paper (Paper): Paper object containing metadata.
            reference (bool): Whether to include the References section. Defaults to False.

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

        table_spans = DocumentProcessor._collect_table_spans(data['tables'])
        paragraphs = DocumentProcessor._process_paragraphs(data['paragraphs'], table_spans, data['tables'])

        current_section = ""
        current_text = ""
        current_pages = []
        reference_section_found = False

        for para in paragraphs:
            if para['type'] == 'section_heading' or para['type'] == 'title':
                if current_section:
                    if not reference_section_found or reference:
                        docs, full_md_text, largest_doc = DocumentProcessor._add_document(
                            docs, current_text, list(np.unique(current_pages)), paper.source, max_token_size, full_md_text, largest_doc
                        )
                current_section = para['content']
                current_text = f"## {current_section}\n\n"
                current_pages = []
                if not reference and current_section.lower().strip() in ['references', 'bibliography', 'works cited']:
                    reference_section_found = True
            else:
                if not reference_section_found or reference:
                    current_text += para['content']
                    current_pages.append(para['page'])

            if not reference_section_found or reference:
                page_key = str(para['page'])
                page_content[page_key] += para['content']

        # Add the last document
        if current_section and (not reference_section_found or reference):
            docs, full_md_text, largest_doc = DocumentProcessor._add_document(
                docs, current_text, list(np.unique(current_pages)), paper.source, max_token_size, full_md_text, largest_doc
            )

        print(f"Created {len(docs)} docs with a total of {DocumentProcessor.count_tokens(full_md_text)} tokens. Largest doc has {largest_doc} tokens.")
        return docs, page_content, full_md_text


    @staticmethod
    def _process_paragraphs(paragraphs: List[Dict[str, Any]], table_spans: Dict[str, int], tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                elif para.get('role') == 'title':
                    processed.append({
                        'type': 'title',
                        'content': para['content'] + "\n\n",
                        'page': para['bounding_regions'][0]['page_number']
                    })
                elif para.get('role') != 'pageNumber':
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
                    end_of_table = DocumentProcessor._calculate_end_of_table(tables[table_idx])

        return processed

    @staticmethod
    def _split_text(text: str, max_token_size: int) -> List[str]:
        """Split text into parts that fit within the max token size."""
        parts = []
        current_part = ""
        for line in text.split('\n'):
            if DocumentProcessor.count_tokens(current_part + line + '\n') > max_token_size:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = ""
                if DocumentProcessor.count_tokens(line + '\n') > max_token_size:
                    # If a single line is too long, split it
                    words = line.split()
                    for word in words:
                        if DocumentProcessor.count_tokens(current_part + word + ' ') > max_token_size:
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
    
    @staticmethod
    def _add_document(docs: List[Document], text: str, pages: List[int], source_name: str,
                      max_token_size: int, full_md_text: str, largest_doc: int) -> Tuple[List[Document], str, int]:
        """Add a new document to the list, splitting if necessary."""
        tokens = DocumentProcessor.count_tokens(text)
        if tokens <= max_token_size:
            docs.append(Document(page_content=text, metadata={"source": source_name, "pages": pages, "tokens": tokens}))
            full_md_text += text
            largest_doc = max(largest_doc, tokens)
        else:
            # Split the document if it's too large
            parts = DocumentProcessor._split_text(text, max_token_size)
            for part in parts:
                part_tokens = DocumentProcessor.count_tokens(part)
                docs.append(Document(page_content=part, metadata={"source": source_name, "pages": pages, "tokens": part_tokens}))
                full_md_text += part
                largest_doc = max(largest_doc, part_tokens)
        return docs, full_md_text, largest_doc

    @staticmethod
    def _collect_table_spans(tables: List[Dict[str, Any]]) -> Dict[str, int]:
        """Collect spans from tables."""
        spans = {}
        for idx, tab in enumerate(tables):
            if len(tab['spans']) == 1:
                key = str(tab['spans'][0]['offset'])
            else:
                key = str(min(sp['offset'] for sp in tab['spans']))
            spans[key] = idx
        return spans

    @staticmethod
    def _calculate_end_of_table(table: Dict[str, Any]) -> int:
        """Calculate the end offset of a table."""
        if len(table['spans']) > 1:
            return min(sp['offset'] for sp in table['spans']) + sum(sp['length'] for sp in table['spans']) + 1
        else:
            return table['spans'][0]['offset'] + table['spans'][0]['length'] + 1

    
