from autosearch.project_config import ProjectConfig
from autosearch.functions.base_function import BaseFunction
from autosearch.data.paper import Paper
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
    paper_db = project_config.paper_db
    project_dir = project_config.project_dir

    if not os.path.exists(local_folder):
        return f"Error: The folder {local_folder} does not exist."

    pdf_files = [f for f in os.listdir(local_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        return f"No PDF files found in {local_folder}."

    processed_files = []
    skipped_files = []
    errors = []

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}...")
        pdf_path = os.path.join(local_folder, pdf_file)

        # Check if the file is already in the database
        if paper_db.check_paper(pdf_path, "read_papers"):
            skipped_files.append(pdf_file)
            print(f"Skipping {pdf_file} as it is already processed.")
            continue

        pdf_filename = os.path.basename(pdf_path)
        # add .pdf extension if missing
        if not pdf_filename.endswith('.pdf'):
            pdf_filename += '.pdf'
        output_pdf_path = os.path.join(project_dir, 'output', pdf_filename)
        if paper_db.check_paper_by_localpath(pdf_path) or paper_db.check_paper_by_localpath(output_pdf_path):
            skipped_files.append(pdf_file)
            print(f"Skipping {pdf_file} as it is already in the database.")
            continue

        try:
            paper = Paper(
                title=os.path.splitext(pdf_file)[0],
                authors=[],
                url=pdf_path,
                source='local'
            )
            processed_paper = document_analyzer.process_local_pdf(paper, project_config)
            processed_files.append(processed_paper.title)
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
            errors.append(f"Error processing {pdf_file}: {str(e)}")

    result = f"Processed {len(processed_files)} files: {', '.join(processed_files)}\n"
    if skipped_files:
        result += f"Skipped {len(skipped_files)} already processed files: {', '.join(skipped_files)}\n"
    if errors:
        result += f"Encountered {len(errors)} errors:\n" + "\n".join(errors)

    return result
