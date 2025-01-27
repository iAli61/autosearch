import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
from typing import Tuple, List, Dict
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from .document_element_type import DocumentElementType
from .document_element_record import DocumentElementRecord, BoundingBox
from .layout_detection_service import LayoutDetectionService
from .nougat_service import NougatService
from .document_types import DocumentElement

class EnhancedDocumentAnalyzer:
    def __init__(self, 
                 api_key: str, 
                 endpoint: str, 
                 output_dir: str = "output",
                 confidence_threshold: float = 0.7):
        """Initialize the document analyzer with both Azure and local services."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Azure Document Intelligence client
        self.azure_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))
        
        # Layout detection for images and tables
        self.layout_detector = LayoutDetectionService(confidence_threshold)
        
        # Initialize Nougat service for complex elements
        self.nougat_service = NougatService()

    def analyze_document(self, pdf_path: str) -> Tuple[str, pd.DataFrame]:
        """
        Analyze a PDF document using both Azure Document Intelligence and local services.
        
        Returns:
            Tuple[str, pd.DataFrame]: Markdown text and elements dataframe
        """
        pdf_path = Path(pdf_path)
        elements = []
        
        # Process with Azure Document Intelligence
        azure_result = self._analyze_with_azure(pdf_path)
        
        # Extract pages from PDF for layout detection
        images = self._pdf_to_images(pdf_path)
        
        # Process each page
        for page_num, page_img in enumerate(images, 1):
            # Get layout elements (images, tables, formulas)
            layout_elements = self.layout_detector.detect_elements(page_img, page_num)
            
            # Save visualization
            vis_path = self.layout_detector.save_page_with_boxes(
                page_img, layout_elements, self.output_dir, page_num
            )
            
            # Process text paragraphs from Azure
            elements.extend(self._process_azure_paragraphs(
                azure_result['paragraphs'], 
                pdf_path.name, 
                page_num
            ))
            
            # Process layout elements
            elements.extend(self._process_layout_elements(
                layout_elements,
                page_img,
                pdf_path.name,
                page_num
            ))

        # Create markdown and DataFrame
        markdown_text = self._create_markdown(elements)
        df = self._create_dataframe(elements)
        
        return markdown_text, df

    def _analyze_with_azure(self, pdf_path: Path) -> Dict:
        """Analyze document with Azure Document Intelligence."""
        with open(pdf_path, "rb") as f:
            poller = self.azure_client.begin_analyze_document(
                "prebuilt-document", document=f)
            result = poller.result()
            return result.to_dict()

    def _process_azure_paragraphs(self, 
                                paragraphs: List[Dict], 
                                pdf_name: str,
                                page_num: int) -> List[DocumentElementRecord]:
        """Process text paragraphs from Azure Document Intelligence."""
        elements = []
        for para in paragraphs:
            if para['bounding_regions'][0]['page_number'] == page_num:
                elements.append(DocumentElementRecord(
                    pdf_file=pdf_name,
                    page=page_num,
                    bounding_box=BoundingBox.from_azure_regions(para['bounding_regions']),
                    element_type=DocumentElementType.TEXT,
                    text=para['content'],
                    role=para['role'],
                    spans=para['spans']
                ))
        return elements


    def _process_layout_elements(self,
                                elements: List[DocumentElement],
                                page_img: Image.Image,
                                pdf_name: str,
                                page_num: int) -> List[DocumentElementRecord]:
        """Process elements detected by LayoutDetectionService with Nougat text extraction."""
        records = []
        
        for elem in elements:
            # Skip text elements as they're handled by Azure
            if elem.label.lower() == 'text':
                continue
                
            # Determine element type and extraction method
            extraction_method = 'default'
            if elem.label.lower() in ['figure', 'image']:
                elem_type = DocumentElementType.IMAGE
            elif elem.label.lower() == 'table':
                elem_type = DocumentElementType.TABLE
                extraction_method = 'nougat'
            elif elem.label.lower() == 'formula':
                elem_type = DocumentElementType.FORMULA
                extraction_method = 'nougat'
            elif elem.label.lower() == 'caption':
                elem_type = self._determine_caption_type(elem, elements)
                extraction_method = 'nougat'
            else:
                continue
                
            # Save element image
            img_path = self._save_element_image(page_img, elem, page_num)
            
            # Extract text using appropriate method
            if extraction_method == 'nougat' and elem_type != DocumentElementType.IMAGE:
                extracted_text = self._extract_text_with_nougat(elem, page_num, img_path, elem_type)
            else:
                extracted_text = None
            
            # Create record with extracted or original text
            records.append(DocumentElementRecord(
                pdf_file=pdf_name,
                page=page_num,
                bounding_box=BoundingBox.from_layout_box(page_num, elem.box),
                element_type=elem_type,
                text=extracted_text if extracted_text else elem.text,
                image_path=img_path,
                confidence=elem.confidence,
                metadata={
                    'extraction_method': extraction_method,
                    'extraction_success': bool(extracted_text)
                }
            ))
            
        return records

    def _extract_text_with_nougat(self, elem, page_num, img_path, elem_type):
        extracted_text = None
        try:
            # Try multiple extraction attempts with error handling
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Process with Nougat
                    extracted_text = self.nougat_service.get_text_from_nougat(img_path)
                    if extracted_text:
                        break
                except AttributeError as ae:
                    # Handle specific model attribute errors
                    if 'pos_drop' in str(ae):
                        print(f"Warning: Known model attribute issue encountered (attempt {attempt + 1}/{max_attempts})")
                        continue
                    else:
                        raise ae
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"Extraction attempt {attempt + 1} failed, retrying...")
                        continue
                    else:
                        print(f"Error extracting text with Nougat for {elem.label} on page {page_num}: {str(e)}")
                        break
            
            if not extracted_text:
                # If Nougat extraction failed, try OCR fallback for tables
                if elem_type == DocumentElementType.TABLE:
                    try:
                        import pytesseract
                        from PIL import Image
                        element_img = Image.open(img_path).convert('RGB')
                        extracted_text = pytesseract.image_to_string(element_img)
                    except Exception as e:
                        print(f"OCR fallback failed for table on page {page_num}: {str(e)}")
                else:
                    print(f"Warning: No text extracted from {elem.label} on page {page_num}")
        except Exception as e:
            print(f"Error processing {elem.label} image on page {page_num}: {str(e)}")
        
        return extracted_text

    def _determine_caption_type(self, 
                              caption_elem: DocumentElement,
                              elements: List[DocumentElement]) -> DocumentElementType:
        """Determine caption type based on proximity to other elements."""
        caption_center = (caption_elem.box[1] + caption_elem.box[3]) / 2
        min_distance = float('inf')
        closest_type = DocumentElementType.IMAGE_CAPTION
        
        for elem in elements:
            if elem.label.lower() in ['figure', 'table', 'formula']:
                elem_center = (elem.box[1] + elem.box[3]) / 2
                distance = abs(elem_center - caption_center)
                
                if distance < min_distance:
                    min_distance = distance
                    if elem.label.lower() == 'table':
                        closest_type = DocumentElementType.TABLE_CAPTION
                    elif elem.label.lower() == 'formula':
                        closest_type = DocumentElementType.FORMULA_CAPTION
                    else:
                        closest_type = DocumentElementType.IMAGE_CAPTION
                        
        return closest_type

    def _save_element_image(self, 
                          page_img: Image.Image, 
                          element: DocumentElement,
                          page_num: int) -> str:
        """Save an element as an image and return the path."""
        # Create directory for element type
        element_dir = self.output_dir / 'elements' / element.label.lower()
        element_dir.mkdir(parents=True, exist_ok=True)
        
        # Crop and save image
        box = [int(c) for c in element.box]
        element_img = page_img.crop(box)
        
        output_path = element_dir / f'page_{page_num}_{element.label}_{id(element)}.png'
        element_img.save(output_path)
        
        return str(output_path)

    def _create_markdown(self, elements: List[DocumentElementRecord]) -> str:
        """Create markdown text from document elements."""
        markdown = []
        current_page = 0
        
        for elem in sorted(elements, key=lambda x: (x.page, x.bounding_box.y1)):
            if elem.page != current_page:
                current_page = elem.page
                markdown.append(f"\n## Page {current_page}\n")
            
            if elem.element_type == DocumentElementType.TEXT:
                markdown.append(elem.text)
            elif elem.element_type in [DocumentElementType.IMAGE, 
                                     DocumentElementType.TABLE, 
                                     DocumentElementType.FORMULA]:
                rel_path = Path(elem.image_path).relative_to(self.output_dir)
                markdown.append(f"\n![]({rel_path})\n")
            elif "caption" in elem.element_type.value:
                markdown.append(f"*{elem.text}*\n")
                
        return "\n".join(markdown)

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
            
        doc.close()
        return images

    def _create_dataframe(self, elements: List[DocumentElementRecord]) -> pd.DataFrame:
        """Create DataFrame from document elements."""
        records = []
        for elem in elements:
            record = {
                'pdf_file': elem.pdf_file,
                'page': elem.page,
                'bounding_box': f"({elem.bounding_box.x1:.2f}, {elem.bounding_box.y1:.2f}, "
                               f"{elem.bounding_box.x2:.2f}, {elem.bounding_box.y2:.2f})",
                'type': elem.element_type.value,
                'text': elem.text,
                'image_path': elem.image_path,
                'role': elem.role,
                'confidence': elem.confidence,
                'spans': str(elem.spans) if elem.spans else None
            }
            records.append(record)
            
        return pd.DataFrame(records)

