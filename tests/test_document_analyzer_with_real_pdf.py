import unittest
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from autosearch.data.paper import Paper
from autosearch.config_types import ProjectConfig
import os
from pathlib import Path
from dotenv import load_dotenv

class TestDocumentAnalyzerWithRealPDF(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.api_key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
        self.endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.project_dir = os.path.join(os.path.dirname(__file__), "test_project_dir")
        self.chunk_pdf_func = lambda paper, config: None  # Replace with your actual chunking function if needed
        self.analyzer = DocumentAnalyzer(self.api_key, self.endpoint, self.project_dir, self.chunk_pdf_func)

    def test_analyze_and_create_docs_with_real_pdf(self):
        paper = Paper(
            title="Real Test Paper",
            url="http://example.com/real_test.pdf",
            local_path=os.path.join(os.path.dirname(__file__), "files/real_test.pdf"),
            authors=["Author Name"],
            source="local"
        )
        pdf_path = os.path.join(os.path.dirname(__file__), "files/real_test.pdf")

        docs, metadata, full_md_text = self.analyzer.analyze_and_create_docs(pdf_path, paper)

        # print("Documents:", docs)
        # print("Metadata:", metadata)
        # print("Full Markdown Text:", full_md_text)

        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(metadata) > 0)
        self.assertTrue(len(full_md_text) > 0)

    def test_pdf2md_chunk_with_real_pdf(self):
        paper = Paper(
            title="Real Test Paper",
            url="http://example.com/real_test.pdf",
            local_path=os.path.join(os.path.dirname(__file__), "files/real_test.pdf"),
            authors=["Author Name"],
            source="local"
        )

        docs = self.analyzer.pdf2md_chunk(paper)

        # print("Documents:", docs)

        self.assertTrue(len(docs) > 0)

    def test_process_local_pdf_with_real_pdf(self):
        paper = Paper(
            title="Real Test Paper",
            url="http://example.com/real_test.pdf",
            local_path=os.path.join(os.path.dirname(__file__), "files/real_test.pdf"),
            authors=["Author Name"],
            source="local"
        )
        project_config = ProjectConfig(
            paper_db="path/to/paper_db",
            doc_analyzer="path/to/doc_analyzer",
            project_dir=self.project_dir,
            db_dir="path/to/db_dir",
            config_list=[],
            initiate_db=False
        )

        updated_paper = self.analyzer.process_local_pdf(paper, project_config)

        # print("Updated Paper Title:", updated_paper.title)
        # print("Updated Paper Abstract:", updated_paper.abstract)

        self.assertTrue(len(updated_paper.title) > 0)
        self.assertTrue(updated_paper.abstract is not None and len(updated_paper.abstract) > 0)

    def test_extract_text_and_title_from_pdf_with_real_pdf(self):
        paper = Paper(
            title="Real Test Paper",
            url="http://example.com/real_test.pdf",
            local_path=os.path.join(os.path.dirname(__file__), "files/real_test.pdf"),
            authors=["Author Name"],
            source="local"
        )

        full_text, title = self.analyzer.extract_text_and_title_from_pdf(paper)

        self.assertTrue(len(full_text) > 0)
        self.assertTrue(len(title) > 0)

    def test_all_pdf_files_in_folder(self):
        files_folder = Path(__file__).parent / "files"
        pdf_files = list(files_folder.glob("*.pdf"))
        for pdf_file in pdf_files:
            with self.subTest(pdf_file=pdf_file):
                paper = Paper(
                    title=pdf_file.stem,
                    url=f"file://{pdf_file}",
                    local_path=str(pdf_file),
                    authors=["Author Name"],
                    source="local"
                )
                
                # Test analyze_and_create_docs
                docs, metadata, full_md_text = self.analyzer.analyze_and_create_docs(str(pdf_file), paper)
                self.assertTrue(len(docs) > 0)
                self.assertTrue(len(metadata) > 0)
                self.assertTrue(len(full_md_text) > 0)

                # Test pdf2md_chunk
                docs = self.analyzer.pdf2md_chunk(paper)
                self.assertTrue(len(docs) > 0)

                # Test process_local_pdf
                project_config = ProjectConfig(
                    paper_db="path/to/paper_db",
                    doc_analyzer="path/to/doc_analyzer",
                    project_dir=self.project_dir,
                    db_dir="path/to/db_dir",
                    config_list=[],
                    initiate_db=False
                )
                updated_paper = self.analyzer.process_local_pdf(paper, project_config)
                self.assertTrue(len(updated_paper.title) > 0)
                self.assertTrue(updated_paper.abstract is not None and len(updated_paper.abstract) > 0)

                # Test extract_text_and_title_from_pdf
                full_text, title = self.analyzer.extract_text_and_title_from_pdf(paper)
                self.assertTrue(len(full_text) > 0)
                self.assertTrue(len(title) > 0)

if __name__ == '__main__':
    unittest.main()
