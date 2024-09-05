from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.exceptions import HttpResponseError
from typing import Dict, Any
import os
import json

class AzureDocumentAnalyzer:
    def __init__(self, api_key: str, endpoint: str):
        self.client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))

    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze a PDF document.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            Dict[str, Any]: The analyzed data from the PDF.

        Raises:
            FileNotFoundError: If the specified PDF file does not exist.
            HttpResponseError: If there's an error in the Azure service request.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")

        try:
            with open(pdf_path, "rb") as f:
                poller = self.client.begin_analyze_document("prebuilt-document", document=f)

            result = poller.result()
            return result.to_dict()
        except HttpResponseError as e:
            print(f"An error occurred: {e}")
            raise


    def save_analysis_result(self, result: Dict[str, Any], output_path: str) -> None:
        """
        Save the analysis result to a JSON file.

        Args:
            result (Dict[str, Any]): The analysis result to save.
            output_path (str): The path where the JSON file should be saved.
        """
        print(f"Saving analysis result to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def load_analysis_result(self, input_path: str) -> Dict[str, Any]:
        """
        Load an analysis result from a JSON file.
        Args:
            input_path (str): The path to the JSON file.
            Returns:
            Dict[str, Any]: The loaded analysis result.
        """
        print(f"Loading analysis result from {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)