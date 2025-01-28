import fitz  # PyMuPDF
import pandas as pd
from typing import Tuple, Dict, List
from pathlib import Path
from dataclasses import dataclass

@dataclass
class BoundingBoxScaler:
    """Handles normalization of bounding boxes from different sources."""
    
    POINTS_PER_INCH = 72  # Standard PDF points per inch
    
    def __init__(self, pdf_path: str):
        """Initialize with PDF path to get actual page dimensions."""
        self.pdf_doc = fitz.open(pdf_path)
        self.page_dimensions = {}
        self.azure_page_dimensions = {}
        
        # Store actual page dimensions (PyMuPDF uses points)
        for page_num, page in enumerate(self.pdf_doc, 1):
            self.page_dimensions[page_num] = {
                'width': page.rect.width,  # in points
                'height': page.rect.height  # in points
            }
    
    def set_azure_dimensions(self, azure_result: Dict):
        """Store Azure-reported page dimensions."""
        for page in azure_result['pages']:
            page_num = page['page_number']
            unit = page['unit'].lower()
            
            if unit != 'inch':
                raise ValueError(f"Unexpected unit from Azure: {unit}. Expected 'inch'")
                
            # Store original dimensions and convert to points
            width_inches = float(page['width'])
            height_inches = float(page['height'])
            
            self.azure_page_dimensions[page_num] = {
                'width_inches': width_inches,
                'height_inches': height_inches,
                'width_points': width_inches * self.POINTS_PER_INCH,
                'height_points': height_inches * self.POINTS_PER_INCH
            }
            
            # Debug logging for dimension comparison
            pdf_width = self.page_dimensions[page_num]['width']
            pdf_height = self.page_dimensions[page_num]['height']
            azure_width_pts = self.azure_page_dimensions[page_num]['width_points']
            azure_height_pts = self.azure_page_dimensions[page_num]['height_points']
            
            print(f"\nPage {page_num} dimensions comparison:")
            print(f"PDF (points): {pdf_width:.2f} x {pdf_height:.2f}")
            print(f"Azure (converted to points): {azure_width_pts:.2f} x {azure_height_pts:.2f}")
            print(f"Azure (original inches): {width_inches:.2f}\" x {height_inches:.2f}\"")
    
    
    def normalize_azure_box(self, page: int, box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """
        Normalize Azure Document Intelligence bounding box.
        Azure provides coordinates in inches, we need to convert to PDF points.
        
        Args:
            page: Page number
            box: (x1, y1, x2, y2) in inches
            
        Returns:
            Coordinates in PDF points
        """
        if page not in self.azure_page_dimensions:
            raise ValueError(f"Azure dimensions not set for page {page}")
            
        # Convert directly from inches to points
        x1_pts = box[0] * self.POINTS_PER_INCH
        y1_pts = box[1] * self.POINTS_PER_INCH
        x2_pts = box[2] * self.POINTS_PER_INCH
        y2_pts = box[3] * self.POINTS_PER_INCH
        
        # Debug logging
        print(f"\nNormalizing Azure box on page {page}:")
        print(f"Original inches: {box}")
        print(f"Converted to points: ({x1_pts:.2f}, {y1_pts:.2f}, {x2_pts:.2f}, {y2_pts:.2f})")
        
        return (x1_pts, y1_pts, x2_pts, y2_pts)
        
        return (x1, y1, x2, y2)
    
    def normalize_layout_box(self, page: int, box: Tuple[float, float, float, float], zoom_factor: float = 3.0) -> Tuple[float, float, float, float]:
        """
        Normalize Layout Detector bounding box.
        Layout detector uses coordinates based on zoomed image dimensions.
        
        Args:
            page: Page number
            box: (x1, y1, x2, y2) in layout detector coordinates (pixels)
            zoom_factor: Zoom factor used when converting PDF to images
            
        Returns:
            Coordinates in PDF points
        """
        # Layout detector coordinates are based on zoomed pixel dimensions
        # Divide by zoom factor to get original PDF point coordinates
        x1 = box[0] / zoom_factor
        y1 = box[1] / zoom_factor
        x2 = box[2] / zoom_factor
        y2 = box[3] / zoom_factor
        
        # Debug logging
        print(f"\nNormalizing Layout box on page {page}:")
        print(f"Original coordinates (pixels): {box}")
        print(f"After normalization (points): ({x1:.2f}pt, {y1:.2f}pt, {x2:.2f}pt, {y2:.2f}pt)")
        
        return (x1, y1, x2, y2)
    
    def normalize_bounding_boxes(self, elements_df: pd.DataFrame, zoom_factor: float = 3.0) -> pd.DataFrame:
        """Normalize all bounding boxes in the elements DataFrame."""
        def parse_box(box_str: str) -> Tuple[float, float, float, float]:
            """Parse bounding box string into tuple."""
            return tuple(float(x.strip()) for x in box_str.strip('()').split(','))
        
        def format_box(box: Tuple[float, float, float, float]) -> str:
            """Format normalized box coordinates as string."""
            return f"({box[0]:.2f}, {box[1]:.2f}, {box[2]:.2f}, {box[3]:.2f})"
        
        normalized_boxes = []
        
        print("\nStarting bounding box normalization...")
        
        for _, row in elements_df.iterrows():
            box = parse_box(row['bounding_box'])
            page = row['page']
            source = row['source']
            
            try:
                print(f"\nProcessing {source} element on page {page}")
                if source == 'azure_document_intelligence':
                    normalized_box = self.normalize_azure_box(page, box)
                elif source == 'layout_detector':
                    normalized_box = self.normalize_layout_box(page, box, zoom_factor)
                else:
                    print(f"Unknown source: {source}, using original coordinates")
                    normalized_box = box
                    
                normalized_boxes.append(format_box(normalized_box))
                
            except Exception as e:
                print(f"Error normalizing box for page {page}: {e}")
                normalized_boxes.append(format_box(box))
        
        elements_df['normalized_box'] = normalized_boxes
        return elements_df

