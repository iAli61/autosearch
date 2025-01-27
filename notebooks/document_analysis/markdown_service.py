from pathlib import Path
from typing import Dict, Any, List
from .document_types import DocumentResult, DocumentElement

class MarkdownService:
    """Service for generating markdown output from document analysis results."""

    def save_results(self, result: DocumentResult, document_name: str):
        """Save analysis results in markdown format."""
        output_path = result.output_dir / f"{document_name}_analysis.md"
        
        with output_path.open('w', encoding='utf-8') as f:
            # Write metadata
            f.write(self._format_metadata(result))
            
            # Write detected elements by page
            f.write(self._format_pages(result))

    def _format_metadata(self, result: DocumentResult) -> str:
        """Format document metadata section."""
        md = "# Document Analysis Results\n\n"
        md += "## Metadata\n"
        
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
                md += f"- **{key}:** {value}\n"
        
        md += "\n"
        return md

    def _format_pages(self, result: DocumentResult) -> str:
        md = "## Document Structure\n\n"
        
        for page in result.pages:
            md += f"### Page {page.page_number}\n\n"
            
            # Sort elements by reading order
            sorted_elements = sorted(page.elements, key=lambda x: x.reading_order)
            
            current_column = -1
            for element in sorted_elements:
                # Add column marker if column changes
                if element.column != current_column:
                    current_column = element.column
                    if len([e for e in page.elements if e.column > 0]) > 0:  # If multi-column
                        md += f"\n#### Column {current_column + 1}\n\n"
                
                # Add element content
                if element.text:
                    if element.label == "Title":
                        md += f"## {element.text}\n\n"
                    elif element.label == "Heading":
                        md += f"### {element.text}\n\n"
                    else:
                        md += f"{element.text}\n\n"
                
                # Add images if present
                if element.path:
                    rel_path = Path(element.path).relative_to(result.output_dir)
                    md += f"\n![{element.label}]({rel_path})\n\n"
            
            md += "\n---\n\n"  # Page separator
        
        return md