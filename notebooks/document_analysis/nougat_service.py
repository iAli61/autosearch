import torch
from PIL import Image
from typing import List, Optional
from nougat import NougatModel
from nougat.postprocessing import markdown_compatible, close_envs
from nougat.utils.checkpoint import get_checkpoint
import os
from .document_types import DocumentElement
from nougat.utils.dataset import ImageDataset
from nougat.utils.device import move_to_device, default_batch_size
from functools import partial

class NougatService:
    """Service for extracting text from document images using Nougat."""
    
    def __init__(self):
        """Initialize the Nougat service."""
        self.checkpoint = get_checkpoint()
        if self.checkpoint is None:
            raise ValueError("Set NOUGAT_CHECKPOINT environment variable!")
            
        # Initialize model
        self.model = NougatModel.from_pretrained(self.checkpoint)
        self.batch_size = default_batch_size()
        self.model = move_to_device(self.model, cuda=self.batch_size > 0)
        if self.batch_size <= 0:
            self.batch_size = 1
        self.model.eval()

    def get_text_from_nougat(self, image_path: str) -> str:
        """
        Extract text from an image using Nougat.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Extracted text in markdown format
        """
        try:
            # Load and process image
            image = Image.open(image_path)
            
            # Create dataset with single image
            dataset = ImageDataset(
                [image_path],
                partial(self.model.encoder.prepare_input, random_padding=False),
            )

            # Create dataloader
            dataloader = torch.utils.data.DataLoader(
                dataset,
                batch_size=self.batch_size,
                pin_memory=True,
                shuffle=False,
            )

            # Process image
            predictions = []
            for sample in dataloader:
                if sample is None:
                    continue
                    
                model_output = self.model.inference(image_tensors=sample)
                
                for output, repeats, repetitions in zip(
                    model_output["predictions"],
                    model_output["repeats"],
                    model_output["repetitions"]
                ):
                    # Handle repetitions and errors
                    if repeats is not None:
                        if repeats > 0:
                            disclaimer = "\n\n+++ ==WARNING: Truncated because of repetitions==\n%s\n+++\n\n"
                        else:
                            disclaimer = "\n\n+++ ==ERROR: No output for this page==\n%s\n+++\n\n"
                        
                        rest = close_envs(repetitions).strip()
                        if len(rest) > 0:
                            disclaimer = disclaimer % rest
                        else:
                            disclaimer = ""
                    else:
                        disclaimer = ""

                    predictions.append(markdown_compatible(output) + disclaimer)

            return "".join(predictions).strip()

        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return ""

    def process_element(self, element):
        try:
            element.text = self.get_text_from_nougat(element.path)
        except Exception as e:
            print(f"Error processing {element.label}: {str(e)}")
            element.text = None
        return element

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
                element = self.process_element(element)
        
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

    def get_text_from_image(self, image_path: str) -> str:
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.model.encoder.prepare_input(image).to(self.device).unsqueeze(0)
            with torch.no_grad():
                output = self.model.inference(image_tensors=inputs)
            prediction = output["predictions"][0]
            if prediction:
                return markdown_compatible(prediction)
            return ""
        except Exception as e:
            print(f"Nougat inference error: {e}")
            return ""