from dataclasses import dataclass
from typing import Optional, List, Dict
from .document_element_type import DocumentElementType

@dataclass
class BoundingBox:
    page: int
    x1: float
    y1: float
    x2: float
    y2: float
    
    @classmethod
    def from_azure_regions(cls, regions: List[Dict]) -> 'BoundingBox':
        region = regions[0]  # Take first region
        polygon = region['polygon']
        return cls(
            page=region['page_number'],
            x1=min(p['x'] for p in polygon),
            y1=min(p['y'] for p in polygon),
            x2=max(p['x'] for p in polygon),
            y2=max(p['y'] for p in polygon)
        )
    
    @classmethod
    def from_layout_box(cls, page: int, box: List[float]) -> 'BoundingBox':
        return cls(
            page=page,
            x1=box[0],
            y1=box[1],
            x2=box[2],
            y2=box[3]
        )

@dataclass
class DocumentElementRecord:
    pdf_file: str
    page: int
    bounding_box: BoundingBox
    element_type: DocumentElementType
    text: Optional[str] = None
    image_path: Optional[str] = None
    role: Optional[str] = None
    confidence: Optional[float] = None
    spans: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None