from transformers import AutoImageProcessor, DeformableDetrForObjectDetection
import torch
from PIL import Image
from typing import List
from pathlib import Path
import os

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