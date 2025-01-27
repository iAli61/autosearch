import torch
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from typing import List, Dict, Any, Tuple
import os
from pathlib import Path
from dataclasses import dataclass
from transformers import AutoImageProcessor, DeformableDetrForObjectDetection
from nougat import NougatModel
from nougat.postprocessing import markdown_compatible, close_envs
from nougat.utils.dataset import ImageDataset
from nougat.utils.checkpoint import get_checkpoint
from functools import partial
from torch.utils.data import DataLoader


@dataclass
class DocumentElement:
    """Represents a detected element in the document with its properties and content."""
    label: str              # Type of element (Text, Title, Figure, etc.)
    confidence: float       # Detection confidence score
    box: List[float]       # Bounding box coordinates [x1, y1, x2, y2]
    page: int              # Page number
    text: str = ""         # Extracted text content
    path: str = ""         # Path to saved image of element

class DocumentAnalysisPipeline:
    """Pipeline combining layout detection and text extraction for scientific documents."""
    
    def __init__(self, output_dir: str = "output", confidence_threshold: float = 0.7):
        """
        Initialize the document analysis pipeline with needed models and settings.
        
        Args:
            output_dir: Directory for output files
            confidence_threshold: Minimum confidence for element detection
        """
        self.output_dir = output_dir
        self.confidence_threshold = confidence_threshold
        self._setup_directories()
        
        # Initialize layout detection model (Deformable DETR)
        print("Initializing layout detection model...")
        self.layout_processor = AutoImageProcessor.from_pretrained("Aryn/deformable-detr-DocLayNet")
        self.layout_model = DeformableDetrForObjectDetection.from_pretrained("Aryn/deformable-detr-DocLayNet")
        
        # Initialize Nougat model for text extraction
        print("Initializing Nougat model...")
        checkpoint = get_checkpoint()
        if checkpoint is None:
            raise ValueError("Set NOUGAT_CHECKPOINT environment variable!")
            
        self.nougat_model = NougatModel.from_pretrained(checkpoint)
        
        # Move models to appropriate device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.layout_model.to(self.device)
        self.nougat_model.to(self.device)
        self.nougat_model.eval()  # Set to evaluation mode
        
        # Set batch size for Nougat processing
        self.batch_size = 1 if self.device.type == 'cpu' else 4
        
        print(f"Pipeline initialized. Using device: {self.device}")

    def _setup_directories(self):
        """Create necessary output directories."""
        os.makedirs(self.output_dir, exist_ok=True)
        for subdir in ['elements', 'text']:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)

    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF document through the complete analysis pipeline.
        
        Args:
            pdf_path: Path to the input PDF file
            
        Returns:
            Dictionary containing analysis results
        """
        print(f"Processing document: {pdf_path}")
        
        # Convert PDF pages to images
        images = self._pdf_to_images(pdf_path)
        print(f"Converted {len(images)} pages to images")
        
        results = {
            'pages': [],
            'metadata': self._extract_metadata(pdf_path)
        }
        
        # Process each page
        for page_num, page_img in enumerate(images, 1):
            print(f"Processing page {page_num}/{len(images)}")
            
            # Detect layout elements
            elements = self._detect_layout_elements(page_img, page_num)
            
            # Save images of elements
            elements = self._save_elements_as_images(page_img, elements)
            
            # Process text in detected elements
            elements = self._process_elements_with_nougat(elements)
            
            # Add processed page to results
            results['pages'].append({
                'page_number': page_num,
                'elements': [vars(elem) for elem in elements]
            })
        
        # Save results to markdown
        self._save_to_markdown(results, pdf_path)
        
        return results

    def _detect_layout_elements(self, image: Image.Image, page_num: int) -> List[DocumentElement]:
        """
        Detect layout elements using Deformable DETR.
        
        Args:
            image: Page image
            page_num: Current page number
            
        Returns:
            List of detected elements
        """
        try:
            # Prepare input
            inputs = self.layout_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.layout_model(**inputs)
            
            # Post-process results
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.layout_processor.post_process_object_detection(
                outputs, 
                target_sizes=target_sizes, 
                threshold=self.confidence_threshold
            )[0]
            
            # Convert to DocumentElement objects
            elements = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                try:
                    # Convert box tensor to list and ensure 4 coordinates
                    box_coords = box.cpu().numpy().tolist()
                    if len(box_coords) != 4:
                        print(f"Warning: Invalid box coordinates: {box_coords}")
                        continue
                    
                    elements.append(DocumentElement(
                        label=self.layout_model.config.id2label[label.item()],
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

    def _process_elements_with_nougat(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """
        Extract text from elements using Nougat model.
        
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
                    image_tensor = self.nougat_model.encoder.prepare_input(image)
                    if isinstance(image_tensor, tuple):
                        image_tensor = image_tensor[0]
                    image_tensor = image_tensor.unsqueeze(0).to(self.device)
                    
                    # Run inference
                    with torch.no_grad():
                        try:
                            output = self.nougat_model.inference(image_tensors=image_tensor)
                            
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

    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF pages to images optimized for Nougat processing.
        
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
    
    def _save_elements_as_images(self, image: Image.Image, elements: List[DocumentElement]) -> List[DocumentElement]:
        """
        Save individual elements as separate images.
        
        Args:
            image: Original page image
            elements: Detected elements
            
        Returns:
            Updated elements with saved image paths
        """
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
                try:
                    element_image = image.crop((x1, y1, x2, y2))
                    element_path = os.path.join(
                        self.output_dir, 
                        'elements',
                        f'page_{element.page}_{element.label}_{idx}.png'
                    )
                    element_image.save(element_path)
                    element.path = element_path
                except Exception as e:
                    print(f"Error saving element image: {e}")
                    continue
                    
            except Exception as e:
                print(f"Error processing element {idx}: {e}")
                continue
        
        return elements

    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata."""
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'keywords': metadata.get('keywords', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
        }

    def _save_to_markdown(self, results: Dict[str, Any], pdf_path: str):
        """
        Save analysis results in markdown format.
        
        Args:
            results: Analysis results
            pdf_path: Original PDF path
        """
        output_path = os.path.join(self.output_dir, f"{Path(pdf_path).stem}_analysis.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write metadata
            f.write("# Document Analysis Results\n\n")
            f.write("## Metadata\n")
            for key, value in results['metadata'].items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n")
            
            # Write detected elements by page
            f.write("## Document Structure\n\n")
            for page in results['pages']:
                f.write(f"### Page {page['page_number']}\n\n")
                
                # Group elements by type
                elements_by_type = {}
                for element in page['elements']:
                    if element['label'] not in elements_by_type:
                        elements_by_type[element['label']] = []
                    elements_by_type[element['label']].append(element)
                
                # Write elements grouped by type
                for label, elements in elements_by_type.items():
                    f.write(f"#### {label}s\n\n")
                    for element in elements:
                        f.write(f"- Confidence: {element['confidence']:.3f}\n")
                        f.write(f"- Location: {[round(x, 2) for x in element['box']]}\n")
                        if element['text']:
                            f.write(f"- Content:\n```\n{element['text']}\n```\n")
                        if element['path']:
                            f.write(f"\n![{label}]({element['path']})\n")
                        f.write("\n")


def analyze_document(pdf_path: str, output_dir: str = "output", confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Analyze a scientific document using layout detection and OCR.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory for output files
        confidence_threshold: Minimum confidence score for detection
        
    Returns:
        Dictionary containing analysis results
    """
    pipeline = DocumentAnalysisPipeline(
        output_dir=output_dir,
        confidence_threshold=confidence_threshold
    )
    results = pipeline.process_document(pdf_path)
    print(f"\nAnalysis complete. Results saved in {output_dir}")
    return results