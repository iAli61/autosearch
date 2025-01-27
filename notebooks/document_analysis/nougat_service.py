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
    
    def __init__(self):
        """Initialize the Nougat service."""
        print("Initializing Nougat model...")
        checkpoint = get_checkpoint()
        if checkpoint is None:
            raise ValueError("Set NOUGAT_CHECKPOINT environment variable!")
            
        self.model = NougatModel.from_pretrained(checkpoint)
        
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
        text_elements = ['Text', 'Title', 'Caption', 'List']
        
        for element in elements:
            if element.label in text_elements and element.path and os.path.exists(element.path):
                try:
                    # Read and process image
                    image = Image.open(element.path).convert('RGB')
                    
                    # Prepare input
                    image_tensor = self.model.encoder.prepare_input(image)
                    if isinstance(image_tensor, tuple):
                        image_tensor = image_tensor[0]
                    image_tensor = image_tensor.unsqueeze(0).to(self.device)
                    
                    # Run inference
                    with torch.no_grad():
                        try:
                            output = self.model.inference(image_tensors=image_tensor)
                            
                            prediction = output["predictions"][0]
                            repeats = output.get("repeats", [None])[0]
                            
                            if repeats is not None:
                                if repeats > 0:
                                    disclaimer = "\n\n+++ ==WARNING: Truncated because of repetitions==\n%s\n+++\n\n"
                                else:
                                    disclaimer = "\n\n+++ ==ERROR: No output for this element==\n%s\n+++\n\n"
                                
                                rest = close_envs(output.get("repetitions", [""])[0]).strip()
                                if rest:
                                    disclaimer = disclaimer % rest
                                else:
                                    disclaimer = ""
                                
                                prediction += disclaimer
                            
                            element.text = markdown_compatible(prediction)
                        except Exception as e:
                            print(f"Nougat inference error: {e}")
                            element.text = f"Error during inference: {str(e)}"
                    
                except Exception as e:
                    print(f"Error processing {element.label}: {str(e)}")
                    element.text = f"Processing error: {str(e)}"
        
        return elements