from pathlib import Path
from typing import Dict, Any, List
from .document_types import DocumentResult, DocumentElement

class MarkdownService:
    """Service for generating markdown output from document analysis results."""

    def format_results(self, result: DocumentResult) -> str:
        """Format analysis results as markdown text."""
        md = []
        
        # Add metadata section
        md.extend(self._format_metadata(result))
        
        # Add document structure section
        md.extend(self._format_pages(result))
        
        return "\n".join(md)

    def save_results(self, result: DocumentResult, document_name: str):
        """Save analysis results to a markdown file."""
        output_path = result.output_dir / f"{document_name}_analysis.md"
        markdown_text = self.format_results(result)
        
        with output_path.open('w', encoding='utf-8') as f:
            f.write(markdown_text)

    def _format_metadata(self, result: DocumentResult) -> List[str]:
        """Format document metadata section."""
        md = ["# Document Analysis Results\n", "## Metadata\n"]
        
        metadata_dict = {
            "Title": result.metadata.title,
            "Author": result.metadata.author,
            "Subject": result.metadata.subject,
            "Keywords": result.metadata.keywords,
            "Creator": result.metadata.creator,
            "Producer": result.metadata.producer,
            "Creation Date": result.metadata.creation_date,
            "Modification Date": result.metadata.modification_date
        }
        
        for key, value in metadata_dict.items():
            if value:  # Only include non-empty values
                md.append(f"- **{key}:** {value}")
        
        md.append("\n")  # Add blank line after metadata
        return md

    def _format_pages(self, result: DocumentResult) -> List[str]:
        """Format document structure section."""
        md = ["## Document Structure\n"]
        
        for page in result.pages:
            md.append(f"### Page {page.page_number}\n")
            
            # Sort elements by reading order
            sorted_elements = sorted(page.elements, key=lambda x: x.reading_order)
            
            current_column = -1
            for element in sorted_elements:
                # Add column marker if column changes
                if element.column != current_column:
                    current_column = element.column
                    if len([e for e in page.elements if e.column > 0]) > 0:  # If multi-column
                        md.append(f"\n#### Column {current_column + 1}\n")
                
                # Format element content
                md.extend(self._format_element(element, result))
            
            md.append("\n---\n")  # Page separator
        
        return md

    def _format_element(self, element: DocumentElement, result: DocumentResult) -> List[str]:
        """Format a single document element."""
        md = []
        
        # Handle text content
        if element.text:
            if element.label == "Title":
                md.append(f"## {element.text}\n")
            elif element.label == "Heading":
                md.append(f"### {element.text}\n")
            else:
                md.append(f"{element.text}\n")
        
        # Handle images and captions
        if element.path:
            rel_path = Path(element.path).relative_to(result.output_dir)
            caption_text = ""
            
            # Add caption if available
            if element.associated_caption:
                caption_text = f" - {element.associated_caption.text}"
            
            md.append(f"\n![{element.label}{caption_text}]({rel_path})\n")
        
        return md