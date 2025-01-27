from typing import List, Tuple
import numpy as np
from collections import defaultdict
from .document_types import DocumentElement

class LayoutAnalyzer:
    """Analyzes page layout to determine column structure and reading order."""
    
    def __init__(self, min_column_gap: float = 50):
        self.min_column_gap = min_column_gap

    def detect_columns(self, elements: List[DocumentElement], page_width: int) -> List[DocumentElement]:
        """Detect column layout and assign column numbers to elements."""
        
        # Skip if no elements
        if not elements:
            return elements

        # Get x-coordinates of all elements
        x_coords = [(elem.box[0], elem.box[2]) for elem in elements]
        
        # Find potential column boundaries using histogram analysis
        x_positions = []
        for start, end in x_coords:
            x_positions.extend([start, end])
        
        hist, bins = np.histogram(x_positions, bins=50)
        gaps = self._find_column_gaps(hist, bins, page_width)
        
        # Assign columns based on element positions
        column_bounds = self._get_column_boundaries(gaps, page_width)
        
        for elem in elements:
            elem.column = self._assign_column(elem.box, column_bounds)
            
        return elements

    def _find_column_gaps(self, hist: np.ndarray, bins: np.ndarray, page_width: int) -> List[float]:
        """Find significant gaps that might indicate column boundaries."""
        gaps = []
        threshold = np.mean(hist) * 0.5
        
        for i in range(len(hist)):
            if hist[i] < threshold:
                gap_center = (bins[i] + bins[i+1]) / 2
                if gap_center > self.min_column_gap and gap_center < (page_width - self.min_column_gap):
                    gaps.append(gap_center)
        
        return gaps

    def _get_column_boundaries(self, gaps: List[float], page_width: int) -> List[Tuple[float, float]]:
        """Convert gap positions into column boundaries."""
        if not gaps:
            return [(0, page_width)]
            
        bounds = []
        last_pos = 0
        
        for gap in sorted(gaps):
            bounds.append((last_pos, gap))
            last_pos = gap
        bounds.append((last_pos, page_width))
        
        return bounds

    def _assign_column(self, box: List[float], column_bounds: List[Tuple[float, float]]) -> int:
        """Assign a column number based on element position."""
        center_x = (box[0] + box[2]) / 2
        
        for i, (start, end) in enumerate(column_bounds):
            if start <= center_x <= end:
                return i
                
        return 0

    def determine_reading_order(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """Determine the reading order of elements within each column."""
        # Group elements by column
        columns = defaultdict(list)
        for elem in elements:
            columns[elem.column].append(elem)
            
        # Sort elements within each column by vertical position
        reading_order = 0
        for column_num in sorted(columns.keys()):
            column_elements = columns[column_num]
            # Sort by y-coordinate (vertical position)
            sorted_elements = sorted(column_elements, key=lambda x: x.box[1])
            
            for elem in sorted_elements:
                elem.reading_order = reading_order
                reading_order += 1
                
        return elements