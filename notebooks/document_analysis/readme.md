# Enhanced Document Analyzer

A powerful document analysis tool that combines Azure Document Intelligence with local layout detection and text extraction capabilities. This tool processes PDF documents to extract text, detect layout elements, and generate comprehensive analysis results.

## Features

- **Multi-Service Integration**: Combines Azure Document Intelligence, local layout detection, and Nougat text extraction
- **Intelligent Layout Analysis**: Detects columns, margins, and document structure
- **Comprehensive Element Detection**: Identifies text, images, tables, formulas, and captions
- **Overlap Resolution**: Smart handling of overlapping elements from different detection sources
- **Visual Debugging**: Generates visualizations of detected elements and layout
- **Markdown Output**: Produces clean, structured markdown output of the analyzed document

## Prerequisites

- Python 3.7+
- Azure Document Intelligence API key and endpoint
- Required Python packages:
  - azure-ai-formrecognizer
  - torch
  - PIL
  - pandas
  - numpy
  - transformers
  - nougat-ocr

## Installation

```bash
pip install azure-ai-formrecognizer torch pillow pandas numpy transformers nougat-ocr
```

## Usage

### Basic Usage

```python
from enhanced_document_analyzer import EnhancedDocumentAnalyzer

# Initialize the analyzer
analyzer = EnhancedDocumentAnalyzer(
    api_key="your_azure_api_key",
    endpoint="your_azure_endpoint",
    output_dir="output",
    confidence_threshold=0.7,
    min_length=10,
    overlap_threshold=0.5
)

# Process a document
markdown_text, elements_df, visualizations = analyzer.analyze_document("path/to/your/document.pdf")

# The results include:
# - markdown_text: A markdown representation of the document
# - elements_df: A DataFrame containing all detected elements and their properties
# - visualizations: Dictionary mapping page numbers to visualization image paths
```

### Advanced Configuration

```python
# Initialize with custom settings
analyzer = EnhancedDocumentAnalyzer(
    api_key="your_azure_api_key",
    endpoint="your_azure_endpoint",
    output_dir="output",
    confidence_threshold=0.8,  # Higher confidence threshold for element detection
    min_length=20,            # Minimum text length to consider
    overlap_threshold=0.6,    # Higher threshold for overlap detection
    ignor_roles=['pageFooter', 'footnote', 'pageHeader']  # Custom roles to ignore
)
```

## Output Structure

### 1. Markdown Text
The generated markdown text includes:
- Document metadata
- Structured content by page and column
- Embedded images and tables
- Extracted formulas and captions

### 2. Elements DataFrame
Contains detailed information about each detected element:
- Position (bounding box coordinates)
- Type (text, image, table, formula, etc.)
- Source (Azure or layout detector)
- Confidence scores
- Extracted text
- Associated metadata

### 3. Visualizations
Debug visualizations showing:
- Detected elements with bounding boxes
- Color-coded element types
- Confidence scores
- Page structure and layout

## Output Directory Structure

```
output/
├── elements/
│   ├── text/
│   ├── images/
│   ├── tables/
│   └── formulas/
├── visualizations/
│   ├── overlays/
│   └── layout/
└── azure_result.json
```

## Example Implementation

```python
from enhanced_document_analyzer import EnhancedDocumentAnalyzer
import pandas as pd

def process_document(pdf_path: str, azure_key: str, azure_endpoint: str):
    # Initialize analyzer
    analyzer = EnhancedDocumentAnalyzer(
        api_key=azure_key,
        endpoint=azure_endpoint,
        output_dir="output"
    )
    
    try:
        # Process document
        markdown_text, elements_df, visualizations = analyzer.analyze_document(pdf_path)
        
        # Save markdown output
        with open("output/analysis.md", "w", encoding="utf-8") as f:
            f.write(markdown_text)
            
        # Save elements data
        elements_df.to_csv("output/elements.csv", index=False)
        
        # Print summary
        print(f"\nProcessing complete!")
        print(f"Total elements detected: {len(elements_df)}")
        print(f"Visualization pages generated: {len(visualizations)}")
        print(f"Results saved to output directory")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")

# Usage
if __name__ == "__main__":
    process_document(
        pdf_path="documents/sample.pdf",
        azure_key="your_key_here",
        azure_endpoint="your_endpoint_here"
    )
```

## Error Handling

The analyzer includes robust error handling:
- Validates input parameters
- Handles missing or corrupted files
- Manages service interruptions
- Provides detailed error messages
- Continues processing when possible

## Performance Considerations

- Processing time depends on document length and complexity
- Azure API calls are cached to avoid redundant processing
- Memory usage scales with document size
- GPU acceleration available for layout detection and Nougat processing
- Consider batch processing for large documents

## Limitations

- Requires Azure Document Intelligence API access
- Complex mathematical formulas may require manual verification
- Processing time increases with document complexity
- Memory requirements scale with page count
- Some advanced layout features may require fine-tuning

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.