from autosearch.project_config import ProjectConfig
from autosearch.functions.base_function import BaseFunction
from typing_extensions import Annotated
import os


class ProcessLocalPDFs(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="process_local_pdfs",
            description="Process PDF files from the local './papers' folder, chunk them, add to memory, and update the paper database.",
            func=process_local_pdfs,
            project_config=project_config
        )


def process_local_pdfs(
    project_config: ProjectConfig,
    local_folder: Annotated[str, "Path to the local folder containing PDFs. Default is './papers'."] = "./papers"
) -> str:
    document_analyzer = project_config.doc_analyzer

    if not os.path.exists(local_folder):
        return f"Error: The folder {local_folder} does not exist."

    pdf_files = [f for f in os.listdir(local_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        return f"No PDF files found in {local_folder}."

    processed_files = []
    errors = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(local_folder, pdf_file)

        try:
            result = document_analyzer.process_local_pdf(pdf_path, project_config)
            processed_files.append(pdf_file)

        except Exception as e:
            errors.append(f"Error processing {pdf_file}: {str(e)}")

    result = f"Processed {len(processed_files)} files: {', '.join(processed_files)}\n"
    if errors:
        result += f"Encountered {len(errors)} errors:\n" + "\n".join(errors)

    return result
