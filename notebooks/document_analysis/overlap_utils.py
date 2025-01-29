import numpy as np
import pandas as pd
from typing import Tuple


def filter_overlapping_elements(df: pd.DataFrame, overlap_threshold: float) -> pd.DataFrame:
    """
    Remove Azure elements that have significant overlap with layout detector elements.
    Preserve Azure ordering by transferring order_id to layout elements.
    
    Args:
        df: DataFrame containing both Azure and layout detector elements
        overlap_threshold: Threshold for determining significant overlap
        
    Returns:
        DataFrame with overlapping Azure elements removed
    """
    # Separate Azure and layout detector elements
    azure_df = df[df['source'] == 'azure_document_intelligence'].copy()
    layout_df = df[df['source'] == 'layout_detector'].copy()
    
    # Initialize mask for elements to keep
    keep_mask = pd.Series(True, index=azure_df.index)
    
    # Initialize azure_order_id for layout elements
    layout_df['azure_order_id'] = float('inf')  # Default to high value
    
    # Check each Azure element against layout detector elements
    for azure_idx, azure_row in azure_df.iterrows():
        azure_box = _parse_box_string(azure_row['normalized_box'])
        azure_page = azure_row['page']
        
        # Only compare with layout elements on the same page
        page_layout = layout_df[layout_df['page'] == azure_page]
        
        for layout_idx, layout_row in page_layout.iterrows():
            layout_box = _parse_box_string(layout_row['normalized_box'])
            
            # Calculate mutual overlap
            overlap_ratio = _calculate_mutual_overlap(azure_box, layout_box)
            
            # If overlap is significant, mark Azure element for removal and transfer order_id
            if overlap_ratio > overlap_threshold:
                # print(f"Found significant overlap ({overlap_ratio:.2f}):")
                # print(f"Azure element: {azure_row['text'][:100]}...")
                # print(f"Layout element: {layout_row['text'][:100] if layout_row['text'] else 'No text'}...")
                keep_mask.at[azure_idx] = False
                
                # Transfer Azure order_id if it's lower than current value
                current_order = layout_df.at[layout_idx, 'azure_order_id']
                new_order = azure_row['azure_order_id']
                if new_order < current_order:
                    layout_df.at[layout_idx, 'azure_order_id'] = new_order
    
    # Combine filtered Azure elements with layout detector elements
    filtered_azure_df = azure_df[keep_mask]
    result_df = pd.concat([filtered_azure_df, layout_df], ignore_index=True)
    
    # Sort by azure_order_id
    result_df = result_df.sort_values(['page', 'azure_order_id'])
    
    return result_df

def _parse_box_string(box_str: str) -> Tuple[float, float, float, float]:
    """Parse a bounding box string into a tuple of coordinates."""
    return tuple(float(x.strip()) for x in box_str.strip('()').split(','))

def _calculate_mutual_overlap(box1: Tuple[float, float, float, float], 
                            box2: Tuple[float, float, float, float]) -> float:
    """
    Calculate mutual overlap ratio between two boxes.
    
    Args:
        box1: First bounding box (x1, y1, x2, y2)
        box2: Second bounding box (x1, y1, x2, y2)
        
    Returns:
        float: Overlap ratio between 0 and 1
    """
    # Calculate intersection coordinates
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    # Check if there is an intersection
    if x2 <= x1 or y2 <= y1:
        return 0.0
    
    # Calculate areas
    intersection = (x2 - x1) * (y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    # Use the minimum area for overlap ratio
    min_area = min(area1, area2)
    
    return intersection / min_area if min_area > 0 else 0.0