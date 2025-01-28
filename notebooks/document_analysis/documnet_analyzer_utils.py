from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import fitz  # PyMuPDF

@dataclass
class BoundingBoxScaler:
    """Handles normalization of bounding boxes from different sources."""
    
    def __init__(self, pdf_path: str):
        """Initialize with PDF path to get actual page dimensions."""
        self.pdf_doc = fitz.open(pdf_path)
        self.page_dimensions = {}
        
        # Store actual page dimensions
        for page_num, page in enumerate(self.pdf_doc, 1):
            self.page_dimensions[page_num] = {
                'width': page.rect.width,
                'height': page.rect.height
            }
    
    def normalize_azure_box(self, page: int, box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """
        Normalize Azure Document Intelligence bounding box.
        Azure uses a 8.5 x 11 inch coordinate system (approximately).
        
        Args:
            page: Page number
            box: (x1, y1, x2, y2) in Azure coordinates
            
        Returns:
            Normalized coordinates in pixels
        """
        page_width = self.page_dimensions[page]['width']
        page_height = self.page_dimensions[page]['height']
        
        # Azure uses roughly 8.5 x 11 inch coordinate system
        azure_width = 8.5
        azure_height = 11.0
        
        # Convert to pixel coordinates
        x1 = (box[0] / azure_width) * page_width
        y1 = (box[1] / azure_height) * page_height
        x2 = (box[2] / azure_width) * page_width
        y2 = (box[3] / azure_height) * page_height
        
        return (x1, y1, x2, y2)
    
    def normalize_layout_box(self, page: int, box: Tuple[float, float, float, float], zoom_factor: float = 3.0) -> Tuple[float, float, float, float]:
        """
        Normalize Layout Detector bounding box.
        Layout detector uses coordinates based on zoomed image dimensions.
        
        Args:
            page: Page number
            box: (x1, y1, x2, y2) in layout detector coordinates
            zoom_factor: Zoom factor used when converting PDF to images (default 3.0)
            
        Returns:
            Normalized coordinates in pixels
        """
        # Layout detector coordinates are based on zoomed image
        # Divide by zoom factor to get original PDF coordinates
        x1 = box[0] / zoom_factor
        y1 = box[1] / zoom_factor
        x2 = box[2] / zoom_factor
        y2 = box[3] / zoom_factor
        
        return (x1, y1, x2, y2)
    
    def normalize_bounding_boxes(self, elements_df, zoom_factor: float = 3.0) -> pd.DataFrame:
        """
        Normalize all bounding boxes in the elements DataFrame.
        
        Args:
            elements_df: DataFrame containing bounding boxes and sources
            zoom_factor: Zoom factor used for layout detection
            
        Returns:
            DataFrame with normalized bounding boxes
        """
        def parse_box(box_str: str) -> Tuple[float, float, float, float]:
            """Parse bounding box string into tuple."""
            return tuple(float(x.strip()) for x in box_str.strip('()').split(','))
        
        def format_box(box: Tuple[float, float, float, float]) -> str:
            """Format normalized box coordinates as string."""
            return f"({box[0]:.2f}, {box[1]:.2f}, {box[2]:.2f}, {box[3]:.2f})"
        
        normalized_boxes = []
        
        for _, row in elements_df.iterrows():
            box = parse_box(row['bounding_box'])
            page = row['page']
            
            if row['source'] == 'azure_document_intelligence':
                normalized_box = self.normalize_azure_box(page, box)
            elif row['source'] == 'layout_detector':
                normalized_box = self.normalize_layout_box(page, box, zoom_factor)
            else:
                normalized_box = box  # Keep as is if source unknown
                
            normalized_boxes.append(format_box(normalized_box))
        
        elements_df['normalized_box'] = normalized_boxes
        return elements_df


class BoundingBoxVisualizer:
    """Service for visualizing and comparing bounding boxes from different sources."""
    
    def __init__(self):
        # Define colors for different sources
        self.colors = {
            'azure_document_intelligence': (255, 0, 0, 128),    # Semi-transparent red
            'layout_detector': (0, 255, 0, 128)                 # Semi-transparent green
        }
        
        # Try to load a font for labels
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            try:
                self.font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                self.font = ImageFont.load_default()

    def create_overlay_visualization(self, 
                                  pdf_path: str,
                                  elements_df: pd.DataFrame,
                                  output_dir: str,
                                  zoom_factor: float = 3.0) -> Dict[int, str]:
        """
        Create visualizations with overlaid bounding boxes from different sources.
        
        Args:
            pdf_path: Path to original PDF
            elements_df: DataFrame with normalized bounding boxes
            output_dir: Directory to save visualizations
            zoom_factor: Zoom factor used for PDF to image conversion
        
        Returns:
            Dict mapping page numbers to visualization paths
        """
        output_dir = Path(output_dir)
        vis_dir = output_dir / 'visualizations' / 'overlays'
        vis_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF pages to images
        doc = fitz.open(pdf_path)
        visualization_paths = {}
        
        # Process each page
        for page_num in range(1, len(doc) + 1):
            # Get page image
            page = doc[page_num - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor), alpha=False)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            # Create transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Filter elements for current page
            page_elements = elements_df[elements_df['page'] == page_num]
            
            # Draw boxes from each source
            for _, element in page_elements.iterrows():
                color = self.colors[element['source']]
                box = self._parse_box(element['normalized_box'])
                
                # Scale box coordinates for zoomed image
                scaled_box = tuple(coord * zoom_factor for coord in box)
                
                # Draw box with transparency
                draw.rectangle(scaled_box, outline=color, fill=(*color[:3], 32), width=2)
                
                # Add label
                label = f"{element['type']} ({element['source'][:5]})"
                label_pos = (scaled_box[0], scaled_box[1] - 20)
                text_bbox = draw.textbbox(label_pos, label, font=self.font)
                draw.rectangle(text_bbox, fill=(*color[:3], 192))
                draw.text(label_pos, label, fill=(255, 255, 255), font=self.font)
            
            # Combine original image with overlay
            result = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # Save visualization
            output_path = vis_dir / f'page_{page_num}_overlay.png'
            result.convert('RGB').save(output_path)
            visualization_paths[page_num] = str(output_path)
            
            # Add legend
            self._add_legend(result, list(self.colors.keys()))
            
        doc.close()
        return visualization_paths
    
    def _parse_box(self, box_str: str) -> Tuple[float, float, float, float]:
        """Parse bounding box string into tuple."""
        return tuple(float(x.strip()) for x in box_str.strip('()').split(','))
    
    def _add_legend(self, img: Image.Image, sources: List[str]):
        """Add legend to the visualization."""
        draw = ImageDraw.Draw(img)
        
        # Legend position
        x = 10
        y = 10
        box_size = 20
        spacing = 5
        
        for source in sources:
            color = self.colors[source]
            
            # Draw color box
            draw.rectangle(
                [(x, y), (x + box_size, y + box_size)],
                fill=(*color[:3], 128),
                outline=(*color[:3], 255)
            )
            
            # Draw label
            draw.text(
                (x + box_size + spacing, y),
                source,
                fill=(0, 0, 0),
                font=self.font
            )
            
            y += box_size + spacing * 2