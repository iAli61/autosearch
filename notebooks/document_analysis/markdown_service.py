from pathlib import Path
from typing import Dict, Any, List
from .document_types import DocumentResult, DocumentElement

class MarkdownService:
    """Service for generating markdown output from document analysis results."""

    def save_results(self, result: DocumentResult, document_name: str):
        """
        Save analysis results in markdown format.
        
        Args:
            result: Analysis results
            document_name: Name of the document (without extension)
        """
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
        """Format document structure section with pages and elements."""
        md = "## Document Structure\n\n"
        
        for page in result.pages:
            md += f"### Page {page.page_number}\n\n"
            
            # Group elements by type
            elements_by_type = self._group_elements_by_type(page.elements)
            
            # Write elements grouped by type
            for label, elements in elements_by_type.items():
                md += self._format_element_group(label, elements, result.output_dir)
        
        return md

    def _group_elements_by_type(self, elements: List[DocumentElement]) -> Dict[str, List[DocumentElement]]:
        """Group elements by their label type."""
        grouped = {}
        for element in elements:
            if element.label not in grouped:
                grouped[element.label] = []
            grouped[element.label].append(element)
        return grouped

    def _format_element_group(self, label: str, elements: List[DocumentElement], output_dir: Path) -> str:
        """Format a group of elements with the same label."""
        md = f"#### {label}s\n\n"
        
        for element in elements:
            md += f"- Confidence: {element.confidence:.3f}\n"
            md += f"- Location: {[round(x, 2) for x in element.box]}\n"
            
            if element.text:
                md += f"- Content:\n```\n{element.text}\n```\n"
            
            if element.path:
                # Convert absolute path to relative path for markdown
                rel_path = Path(element.path).relative_to(output_dir)
                md += f"\n![{label}]({rel_path})\n"
            
            md += "\n"
        
        return md

    def _format_timestamp(self, timestamp: str) -> str:
        """Format a PDF timestamp into a readable string."""
        # Remove PDF date format markers if present
        if timestamp.startswith('D:'):
            timestamp = timestamp[2:]
        return timestamp