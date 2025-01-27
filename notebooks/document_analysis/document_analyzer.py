import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any
import os

from .document_types import (
    DocumentElement, 
    PageResult, 
    DocumentMetadata, 
    DocumentResult
)
from .layout_detection_service import LayoutDetectionService
from .nougat_service import NougatService
from .markdown_service import MarkdownService
from .layout_analyzer import LayoutAnalyzer

class DocumentAnalyzer:
    def __init__(self, output_dir: str = "output", confidence_threshold: float = 0.7):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.layout_detector = LayoutDetectionService(confidence_threshold)
        self.layout_analyzer = LayoutAnalyzer()
        self.nougat_service = NougatService()
        self.markdown_service = MarkdownService()

    def analyze_document(self, pdf_path: str) -> DocumentResult:
        pdf_path = Path(pdf_path)
        print(f"Processing document: {pdf_path}")
        
        # Convert PDF pages to images
        images = self._pdf_to_images(pdf_path)
        print(f"Converted {len(images)} pages to images")
        
        # Extract metadata
        metadata = self._extract_metadata(pdf_path)
        
        # Process each page
        pages = []
        for page_num, page_img in enumerate(images, 1):
            print(f"Processing page {page_num}/{len(images)}")
            
            # Detect layout elements
            elements = self.layout_detector.detect_elements(page_img, page_num)
            
            # Analyze page layout and determine reading order
            elements = self.layout_analyzer.detect_columns(elements, page_img.width)
            elements = self.layout_analyzer.determine_reading_order(elements)
            
            # Save visualization of the page with bounding boxes
            vis_path = self.layout_detector.save_page_with_boxes(
                page_img,
                elements,
                self.output_dir,
                page_num
            )
            print(f"Saved page visualization to: {vis_path}")
            
            # Save individual element images
            elements = self.layout_detector.save_elements_as_images(
                page_img, 
                elements, 
                self.output_dir
            )
            
            # Process text in detected elements
            elements = self.nougat_service.process_elements(elements)
            
            # Sort elements by reading order
            elements = sorted(elements, key=lambda x: x.reading_order)
            
            # Add processed page to results
            pages.append(PageResult(page_number=page_num, elements=elements))
        
        # Create final result
        result = DocumentResult(
            metadata=metadata,
            pages=pages,
            output_dir=self.output_dir
        )
        
        # Save results to markdown
        self.markdown_service.save_results(result, pdf_path.stem)
        
        return result
    def _pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """
        Convert PDF pages to images optimized for processing.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of page images
        """
        doc = fitz.open(pdf_path)
        images = []
        
        for page in doc:
            # Use a higher DPI for better text recognition (300 DPI)
            zoom = 3.0  # 72 dpi * 3 = 216 dpi
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert to PIL Image in RGB mode
            img = Image.frombytes(
                'RGB',
                [pix.width, pix.height],
                pix.samples
            )
            
            images.append(img)
        
        return images
    
    def _extract_metadata(self, pdf_path: Path) -> DocumentMetadata:
        """
        Extract PDF metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            DocumentMetadata
        """
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        return DocumentMetadata(
            title=metadata.get('title', ''),
            author=metadata.get('author', ''),
            subject=metadata.get('subject', ''),
            keywords=metadata.get('keywords', ''),
            creator=metadata.get('creator', ''),
            producer=metadata.get('producer', ''),
            creation_date=metadata.get('creationDate', ''),
            modification_date=metadata.get('modDate', '')
        )