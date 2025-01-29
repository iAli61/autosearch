
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import List, Dict
from .document_element_record import DocumentElementRecord, BoundingBox
from .document_element_type import DocumentElementType
import json
import os

def analyze_with_azure(azure_client: DocumentAnalysisClient, pdf_path: str, output_dir: str) -> dict:
    """Analyze document with Azure Document Intelligence."""

    # Check if the analysis result already exists
    if os.path.exists(f"{output_dir}/azure_result.json"):
        print(f"Loading analysis result from {output_dir}/azure_result.json")
        with open(f"{output_dir}/azure_result.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    with open(pdf_path, "rb") as f:
        poller = azure_client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result().to_dict()
        print(f"Saving analysis result to {output_dir}/azure_result.json")
        with open(f"{output_dir}/azure_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        return result

def process_azure_paragraphs(paragraphs: List[Dict], pdf_name: str, page_info: Dict, page_num: int, ignor_roles: List[str], min_length: int) -> List[DocumentElementRecord]:
    """Process text paragraphs from Azure Document Intelligence."""
    elements = []
    
    # Store page dimensions
    page_width = float(page_info['width'])
    page_height = float(page_info['height'])
    page_unit = page_info['unit']
    
    # Add order_id to track original Azure ordering
    for order_id, para in enumerate(paragraphs):
        if para['role'] in ignor_roles:
            continue
        if len(para['content']) < min_length:
            continue
            
        if para['bounding_regions'][0]['page_number'] == page_num:
            elements.append(DocumentElementRecord(
                pdf_file=pdf_name,
                page=page_num,
                bounding_box=BoundingBox.from_azure_regions(para['bounding_regions']),
                element_type=DocumentElementType.TEXT,
                text=para['content'],
                role=para['role'],
                spans=para['spans'],
                metadata={
                    'source': 'azure_document_intelligence',
                    'page_width': page_width,
                    'page_height': page_height,
                    'page_unit': page_unit,
                    'azure_order_id': order_id  # Add order_id to metadata
                }
            ))
    
    return elements