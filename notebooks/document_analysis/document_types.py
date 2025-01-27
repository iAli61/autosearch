from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class DocumentElement:
    """Represents a detected element in the document with its properties and content."""
    label: str              # Type of element (Text, Title, Figure, etc.)
    confidence: float       # Detection confidence score
    box: List[float]       # Bounding box coordinates [x1, y1, x2, y2]
    page: int              # Page number
    text: str = ""         # Extracted text content
    path: str = ""         # Path to saved image of element
    column: int = 0        # Column number (0 for single column)
    reading_order: int = 0  # Position in reading order

@dataclass
class PageResult:
    """Results for a single page."""
    page_number: int
    elements: List[DocumentElement]

@dataclass
class DocumentMetadata:
    """Document metadata extracted from PDF."""
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    modification_date: str = ""

@dataclass
class DocumentResult:
    """Complete analysis results for a document."""
    metadata: DocumentMetadata
    pages: List[PageResult]
    output_dir: Path