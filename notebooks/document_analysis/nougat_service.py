import torch
from PIL import Image
from typing import List
from nougat import NougatModel
from nougat.postprocessing import markdown_compatible, close_envs
from nougat.utils.checkpoint import get_checkpoint
import os

from .document_types import DocumentElement

class NougatService:
    """Service for extracting text from document images using Nougat."""
    
    def __init__(self, checkpoint: str = None):
        """Initialize the Nougat service."""
        print("Initializing Nougat model...")
        if checkpoint is None:
            checkpoint = get_checkpoint()
        if checkpoint is None:
            raise ValueError("Set NOUGAT_CHECKPOINT environment variable!")
            
        # Add ignore_mismatched_sizes=True to handle size mismatches
        self.model = NougatModel.from_pretrained(
            checkpoint,
            ignore_mismatched_sizes=True  # Add this parameter
        )
        
        # Move model to appropriate device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Set batch size based on device
        self.batch_size = 1 if self.device.type == 'cpu' else 4
        
        print(f"Nougat service initialized. Using device: {self.device}")

    def process_elements(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """
        Extract text from document elements using Nougat.
        
        Args:
            elements: List of detected elements
            
        Returns:
            Elements with extracted text
        """
        # Process only text-based elements
        text_elements = ['Text', 'Title', 'Caption', 'List', 'Formula']
        
        for element in elements:
            if element.label in text_elements and element.path and os.path.exists(element.path):
                try:
                    # Read and process image
                    image = Image.open(element.path).convert('RGB')
                    
                    # Prepare input
                    inputs = self.model.encoder.prepare_input(image).to(self.device)
                    inputs = inputs.unsqueeze(0)
                    
                    # Run inference
                    with torch.no_grad():
                        try:
                            output = self.model.inference(image_tensors=inputs)
                            
                            prediction = output["predictions"][0]
                            if prediction:
                                element.text = markdown_compatible(prediction)
                            
                        except Exception as e:
                            print(f"Nougat inference error for {element.label}: {e}")
                            element.text = None
                    
                except Exception as e:
                    print(f"Error processing {element.label}: {str(e)}")
                    element.text = None
        
        return elements

    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from a single image.
        
        Args:
            image: PIL Image to process
            
        Returns:
            str: Extracted text in markdown format
        """
        try:
            # Prepare input
            inputs = self.model.encoder.prepare_input(image).to(self.device)
            inputs = inputs.unsqueeze(0)
            
            # Run inference
            with torch.no_grad():
                output = self.model.inference(image_tensors=inputs)
                prediction = output["predictions"][0]
                
                if prediction:
                    return markdown_compatible(prediction)
                return ""
                
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return ""