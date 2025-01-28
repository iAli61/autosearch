from transformers import AutoImageProcessor, DeformableDetrForObjectDetection
import torch
from PIL import Image, ImageDraw, ImageFont
from typing import List
from pathlib import Path
import os
import random
from .document_types import DocumentElement

class LayoutDetectionService:
    """Service for detecting layout elements in document images using Deformable DETR."""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the layout detection service.
        
        Args:
            confidence_threshold: Minimum confidence for element detection
        """
        self.confidence_threshold = confidence_threshold
        
        # Initialize layout detection model
        print("Initializing layout detection model...")
        self.processor = AutoImageProcessor.from_pretrained("Aryn/deformable-detr-DocLayNet")
        self.model = DeformableDetrForObjectDetection.from_pretrained("Aryn/deformable-detr-DocLayNet")
        
        # Move model to appropriate device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        print(f"Layout detection service initialized. Using device: {self.device}")

        # Define colors for different element types
        self.colors = {
            'Text': (255, 0, 0),      # Red
            'Title': (0, 255, 0),     # Green
            'List': (0, 0, 255),      # Blue
            'Table': (255, 165, 0),   # Orange
            'Figure': (128, 0, 128),  # Purple
            'Caption': (0, 255, 255), # Cyan
            'Header': (255, 192, 203), # Pink
            'Footer': (255, 255, 0),  # Yellow
            'Page_number': (165, 42, 42), # Brown
            'Reference': (0, 128, 0),  # Dark Green
            'Formula': (255, 0, 255),  # Magenta
            'Other': (128, 128, 128)   # Gray
        }

    def save_page_with_boxes(self, 
                            image: Image.Image, 
                            elements: List[DocumentElement], 
                            output_path: str,
                            page_num: int) -> str:
        """
        Save the page image with bounding boxes drawn around detected elements.
        
        Args:
            image: Original page image
            elements: List of detected elements
            output_path: Base directory for output
            page_num: Current page number
            
        Returns:
            str: Path to the saved visualization
        """
        # Create a copy of the image to draw on
        vis_image = image.copy()
        draw = ImageDraw.Draw(vis_image)
        
        # Try to load a font (use default if not available)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                font = ImageFont.load_default()

        # Draw boxes and labels for each element
        for idx, element in enumerate(elements):
            # Get color for this element type
            color = self.colors.get(element.label, (random.randint(0, 255), 
                                                  random.randint(0, 255), 
                                                  random.randint(0, 255)))
            
            # Draw bounding box
            box = element.box
            draw.rectangle(
                [(box[0], box[1]), (box[2], box[3])],
                outline=color,
                width=2
            )
            
            # Draw label with confidence score
            label_text = f"{element.label}: {element.confidence:.2f}"
            text_bbox = draw.textbbox((box[0], box[1]-25), label_text, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text(
                (box[0], box[1]-25),
                label_text,
                fill='white',
                font=font
            )

        # Save the visualization
        vis_dir = Path(output_path) / 'visualizations'
        vis_dir.mkdir(parents=True, exist_ok=True)
        output_file = vis_dir / f'page_{page_num}_layout.png'
        vis_image.save(output_file)
        
        return str(output_file)

    def detect_elements(self, image: Image.Image, page_num: int) -> List[DocumentElement]:
        """
        Detect layout elements in an image.
        
        Args:
            image: Page image
            page_num: Current page number
            
        Returns:
            List of detected elements
        """
        try:
            # Prepare input
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Post-process results
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.processor.post_process_object_detection(
                outputs, 
                target_sizes=target_sizes, 
                threshold=self.confidence_threshold
            )[0]
            
            # Convert to DocumentElement objects
            elements = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                try:
                    box_coords = box.cpu().numpy().tolist()
                    if len(box_coords) != 4:
                        print(f"Warning: Invalid box coordinates: {box_coords}")
                        continue
                    
                    elements.append(DocumentElement(
                        label=self.model.config.id2label[label.item()],
                        confidence=score.item(),
                        box=box_coords,
                        page=page_num
                    ))
                except Exception as e:
                    print(f"Error creating document element: {e}")
                    continue
            
            return elements
            
        except Exception as e:
            print(f"Error in layout detection: {e}")
            return []

    def save_elements_as_images(self, 
                              image: Image.Image, 
                              elements: List[DocumentElement], 
                              output_dir: Path) -> List[DocumentElement]:
        """
        Save individual elements as separate images.
        
        Args:
            image: Original page image
            elements: Detected elements
            output_dir: Directory to save element images
            
        Returns:
            Updated elements with saved image paths
        """
        elements_dir = output_dir / 'elements'
        elements_dir.mkdir(parents=True, exist_ok=True)

        for idx, element in enumerate(elements):
            try:
                # Get coordinates and ensure they're within image bounds
                box = element.box
                x1, y1, x2, y2 = (
                    max(0, int(box[0])),
                    max(0, int(box[1])),
                    min(image.width, int(box[2])),
                    min(image.height, int(box[3]))
                )
                
                # Skip if box is invalid
                if x2 <= x1 or y2 <= y1:
                    print(f"Warning: Invalid box coordinates for {element.label}: {box}")
                    continue
                
                # Crop and save element
                element_image = image.crop((x1, y1, x2, y2))
                element_path = elements_dir / f'page_{element.page}_{element.label}_{idx}.png'
                element_image.save(element_path)
                element.path = str(element_path)
                    
            except Exception as e:
                print(f"Error processing element {idx}: {e}")
                continue
        
        return elements