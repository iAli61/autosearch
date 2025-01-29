from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

@dataclass
class PageDimensions:
    """Represents page dimensions in both inches and pixels."""
    width_inches: float
    height_inches: float
    width_pixels: float  # width in points (72 points per inch)
    height_pixels: float  # height in points
    
    @classmethod
    def from_dataframe_row(cls, row: pd.Series) -> 'PageDimensions':
        width_inches = float(row['page_width'])
        height_inches = float(row['page_height'])
        return cls(
            width_inches=width_inches,
            height_inches=height_inches,
            width_pixels=width_inches * 72,
            height_pixels=height_inches * 72
        )

@dataclass
class MarginSizes:
    """Represents margin sizes as ratios of page dimensions."""
    left: float
    right: float
    top: float
    bottom: float
    
    def validate(self, min_ratio: float = 0.05, max_ratio: float = 0.15) -> 'MarginSizes':
        """
        Validate and clip margin ratios to acceptable ranges.
        Typical documents have margins between 5-15% of page dimensions.
        """
        return MarginSizes(
            left=np.clip(self.left, min_ratio, max_ratio),
            right=np.clip(self.right, min_ratio, max_ratio),
            top=np.clip(self.top, min_ratio, max_ratio),
            bottom=np.clip(self.bottom, min_ratio, max_ratio)
        )
    
    def to_pixels(self, dimensions: PageDimensions) -> Dict[str, float]:
        """Convert margin ratios to pixel values."""
        return {
            'left': self.left * dimensions.width_pixels,
            'right': dimensions.width_pixels * (1 - self.right),
            'top': self.top * dimensions.height_pixels,
            'bottom': dimensions.height_pixels * (1 - self.bottom)
        }

@dataclass
class ColumnLayout:
    """Represents the detected column layout of the document."""
    num_columns: int
    column_positions: List[Tuple[float, float]]  # List of (start, end) positions in pixels
    
    def is_in_margin(self, x: float, page_width: float) -> bool:
        """Check if an x-coordinate falls between columns or outside content area."""
        if not self.column_positions:
            return False
            
        # Check if position is between columns
        for i in range(len(self.column_positions) - 1):
            col_end = self.column_positions[i][1]
            next_col_start = self.column_positions[i + 1][0]
            if col_end < x < next_col_start:
                return True
                
        # Check if position is outside the content area
        first_col_start = self.column_positions[0][0]
        last_col_end = self.column_positions[-1][1]
        return x < first_col_start or x > last_col_end

class MarginDetector:
    """Handles detection and filtering of page margins in documents."""
    
    def __init__(self, 
                 density_bins: int = 100,
                 min_column_gap: float = 50,  # minimum gap between columns in pixels
                 peak_prominence: float = 0.1):  # minimum prominence for peak detection
        self.density_bins = density_bins
        self.min_column_gap = min_column_gap
        self.peak_prominence = peak_prominence
    
    def _detect_columns(self, 
                       edges: Dict[str, np.ndarray], 
                       dimensions: PageDimensions) -> ColumnLayout:
        """
        Detect document columns using density-based analysis of x-coordinates.
        """
        # Create density histogram of x-coordinates
        x_positions = np.concatenate([edges['left'], edges['right']])
        hist, bin_edges = np.histogram(x_positions, bins=self.density_bins, 
                                     range=(0, dimensions.width_pixels))
        
        # Smooth histogram for better peak detection
        smoothed_hist = np.convolve(hist, np.ones(5)/5, mode='same')
        
        # Find valleys (low density regions = potential column gaps)
        valleys, _ = find_peaks(-smoothed_hist, 
                              prominence=self.peak_prominence * np.max(smoothed_hist))
        
        if len(valleys) == 0:
            # Single column document
            return ColumnLayout(
                num_columns=1,
                column_positions=[(0, dimensions.width_pixels)]
            )
        
        # Convert valley indices to x-coordinates
        valley_positions = bin_edges[valleys]
        
        # Filter valleys by minimum gap width
        significant_valleys = []
        for i in range(len(valley_positions) - 1):
            gap_width = valley_positions[i + 1] - valley_positions[i]
            if gap_width >= self.min_column_gap:
                significant_valleys.append(valley_positions[i])
        
        # Determine column boundaries
        column_positions = []
        last_pos = 0
        for valley in significant_valleys:
            column_positions.append((last_pos, valley))
            last_pos = valley
        column_positions.append((last_pos, dimensions.width_pixels))
        
        return ColumnLayout(
            num_columns=len(column_positions),
            column_positions=column_positions
        )
    
    def detect_margins(self, df: pd.DataFrame) -> Tuple[Dict[int, MarginSizes], ColumnLayout]:
        """
        Detect consistent margin sizes and column layout across all pages.
        """
        # Collect edge positions from all pages
        all_edges = {
            'left': [],
            'right': [],
            'top': [],
            'bottom': []
        }
        
        # Use first row for dimensions since pages should be same size
        dimensions = PageDimensions.from_dataframe_row(df.iloc[0])
        
        # Collect edges from all pages
        for _, page_df in df.groupby('page'):
            edges = self._collect_edge_positions(page_df)
            for edge_type in all_edges:
                all_edges[edge_type].extend(edges[edge_type])
                
        # Convert lists to numpy arrays
        all_edges = {edge: np.array(positions) for edge, positions in all_edges.items()}
        
        # Detect column layout first
        column_layout = self._detect_columns(all_edges, dimensions)
        
        # Calculate margins based on content distribution and column layout
        document_margins = self._calculate_margins(all_edges, dimensions, column_layout)
        
        # Apply same margins to all pages
        margin_sizes = {}
        for page_num in df['page'].unique():
            margin_sizes[page_num] = document_margins
            
        # Log the results
        self._log_detection_results(document_margins, column_layout, dimensions)
        
        return margin_sizes, column_layout
    
    def _calculate_margins(self, 
                         edges: Dict[str, np.ndarray], 
                         dimensions: PageDimensions,
                         column_layout: ColumnLayout) -> MarginSizes:
        """Calculate margin sizes considering column layout."""
        # For left/right margins, use the column boundaries
        if column_layout.column_positions:
            left_margin = column_layout.column_positions[0][0] / dimensions.width_pixels
            right_margin = (dimensions.width_pixels - column_layout.column_positions[-1][1]) / dimensions.width_pixels
        else:
            # Fallback to percentile method
            left_margin = np.percentile(edges['left'], 5) / dimensions.width_pixels
            right_margin = 1 - (np.percentile(edges['right'], 95) / dimensions.width_pixels)
        
        # For top/bottom margins, use content distribution
        top_margin = np.percentile(edges['top'], 5) / dimensions.height_pixels
        bottom_margin = 1 - (np.percentile(edges['bottom'], 95) / dimensions.height_pixels)
        
        margins = MarginSizes(
            left=left_margin,
            right=right_margin,
            top=top_margin,
            bottom=bottom_margin
        )
        
        return margins.validate()
    
    def _collect_edge_positions(self, page_df: pd.DataFrame) -> Dict[str, List[float]]:
        """Collect all edge positions from page elements."""
        edges = {edge: [] for edge in ['left', 'right', 'top', 'bottom']}
        
        for _, row in page_df.iterrows():
            box = [float(x.strip()) for x in row['normalized_box'].strip('()').split(',')]
            edges['left'].append(box[0])
            edges['right'].append(box[2])
            edges['top'].append(box[1])
            edges['bottom'].append(box[3])
        
        return edges
    
    def _log_detection_results(self, 
                             margins: MarginSizes, 
                             column_layout: ColumnLayout,
                             dimensions: PageDimensions):
        """Log detection results."""
        print("\nDocument Layout Analysis Results:")
        print(f"Number of columns detected: {column_layout.num_columns}")
        print("\nColumn positions (in pixels):")
        for i, (start, end) in enumerate(column_layout.column_positions):
            print(f"Column {i+1}: {start:.1f} to {end:.1f}")
        
        print("\nDetected margins (as ratio of page dimensions):")
        print(f"Left margin: {margins.left:.4f}")
        print(f"Right margin: {margins.right:.4f}")
        print(f"Top margin: {margins.top:.4f}")
        print(f"Bottom margin: {margins.bottom:.4f}")
        
        margin_pixels = margins.to_pixels(dimensions)
        print("\nMargins in pixels:")
        print(f"Left margin: {margin_pixels['left']:.1f}px")
        print(f"Right margin: {dimensions.width_pixels - margin_pixels['right']:.1f}px")
        print(f"Top margin: {margin_pixels['top']:.1f}px")
        print(f"Bottom margin: {dimensions.height_pixels - margin_pixels['bottom']:.1f}px")
        
        print(f"\nPage dimensions: {dimensions.width_inches}\" x {dimensions.height_inches}\"")

    def filter_margin_elements(self, 
                             df: pd.DataFrame, 
                             margin_sizes: Optional[Dict[int, MarginSizes]] = None,
                             column_layout: Optional[ColumnLayout] = None) -> pd.DataFrame:
        """Remove elements that fall within detected page margins or between columns."""
        if margin_sizes is None or column_layout is None:
            margin_sizes, column_layout = self.detect_margins(df)
            
        filtered_df = df.copy()
        stats = {'total': 0, 'removed': 0}
        
        for idx, row in df.iterrows():
            if row['source'] != 'azure_document_intelligence':
                continue
                
            stats['total'] += 1
            page_num = row['page']
            dimensions = PageDimensions.from_dataframe_row(row)
            box = [float(x.strip()) for x in row['normalized_box'].strip('()').split(',')]
            
            # Get margin boundaries
            margins_px = margin_sizes[page_num].to_pixels(dimensions)
            
            # Check if element center is in margins or between columns
            center_x = (box[0] + box[2]) / 2
            center_y = (box[1] + box[3]) / 2
            
            is_in_vertical_margins = (
                center_y < margins_px['top'] or 
                center_y > margins_px['bottom']
            )
            
            is_in_horizontal_margins = (
                center_x < margins_px['left'] or
                center_x > margins_px['right'] or
                column_layout.is_in_margin(center_x, dimensions.width_pixels)
            )
            
            if is_in_vertical_margins or is_in_horizontal_margins:
                filtered_df.drop(idx, inplace=True)
                stats['removed'] += 1
        
        # Log statistics
        if stats['total'] > 0:
            removal_ratio = (stats['removed'] / stats['total']) * 100
            print(f"\nMargin filtering summary:")
            print(f"Total elements processed: {stats['total']}")
            print(f"Elements removed: {stats['removed']} ({removal_ratio:.1f}%)")
        
        return filtered_df