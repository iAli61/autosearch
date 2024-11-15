import os
import shutil
from autosearch.data.paper import Paper
from autosearch.api.search_manager import SearchManager

class PDFManager:
    def __init__(self, project_dir: str, output_dir: str):
        self.project_dir = project_dir
        self.output_dir = output_dir
        self.search_manager = SearchManager(project_dir)

    def handle_local_pdf(self, paper: Paper) -> str:
        """
        Handle local PDF files.
        
        Args:
            paper (Paper): The paper object containing local file information.
        
        Returns:
            str: The path to the PDF file in the output directory.
        
        Raises:
            FileNotFoundError: If the local PDF file doesn't exist.
        """
        source_path = paper.local_path if paper.local_path and os.path.exists(paper.local_path) else paper.url
        pdf_filename = os.path.basename(source_path)
        output_path = os.path.join(self.output_dir, pdf_filename)

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Local PDF file not found: {source_path}")

        if not os.path.exists(output_path):
            shutil.copy2(source_path, output_path)
            paper.local_path = output_path

        return output_path

    def handle_remote_pdf(self, paper: Paper) -> str:
        """
        Handle remote PDF files.
        
        Args:
            paper (Paper): The paper object containing remote file information.
        
        Returns:
            str: The path to the downloaded PDF file in the output directory.
        
        Raises:
            Exception: If there's an error downloading the PDF.
        """
        pdf_filename = os.path.basename(paper.url)
        if not pdf_filename.endswith('.pdf'):
            pdf_filename += '.pdf'
        output_path = os.path.join(self.output_dir, pdf_filename)

        if not os.path.exists(output_path):
            try:
                self.search_manager.download_pdf(paper, self.output_dir)
            except Exception as e:
                raise Exception(f"Error downloading PDF for {paper.title}: {str(e)}")

        paper.local_path = output_path
        return output_path

    def ensure_pdf_exists(self, paper: Paper) -> str:
        """
        Ensure the PDF exists locally, downloading it if necessary.
        
        Args:
            paper (Paper): The paper object.
        
        Returns:
            str: The path to the PDF file.
        
        Raises:
            FileNotFoundError: If the PDF file can't be found or downloaded.
        """
        if paper.source == 'local':
            return self.handle_local_pdf(paper)
        elif paper.url.startswith('http'):
            return self.handle_remote_pdf(paper)
        else:
            raise FileNotFoundError(f"Invalid paper source or URL: {paper.source}, {paper.url}")