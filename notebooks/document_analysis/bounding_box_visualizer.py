from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import fitz  # PyMuPDF

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