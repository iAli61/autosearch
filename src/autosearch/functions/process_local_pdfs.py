from concurrent.futures import ThreadPoolExecutor
from typing_extensions import Annotated
import os
from autosearch.project_config import ProjectConfig
from autosearch.functions.base_function import BaseFunction
from autosearch.data.paper import Paper


class ProcessLocalPDFs(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="process_local_pdfs",
            description="Process PDF files from the local './papers' folder, chunk them, add to memory, and update the paper database.",
            func=process_local_pdfs,
            project_config=project_config
        )


def process_single_pdf(pdf_file: str, local_folder: str, project_config: ProjectConfig):
    document_analyzer = project_config.doc_analyzer
    paper_db = project_config.paper_db
    project_dir = project_config.project_dir

    pdf_path = os.path.join(local_folder, pdf_file)
    pdf_filename = os.path.basename(pdf_path)
    output_pdf_path = os.path.join(project_dir, 'output', pdf_filename)

    if paper_db.check_paper_by_localpath(pdf_path) or paper_db.check_paper_by_localpath(output_pdf_path):
        return f"Skipping {pdf_file} as it is already in the database."

    try:
        paper = Paper(
            title=os.path.splitext(pdf_file)[0],
            authors=[],
            url=pdf_path,
            source='local'
        )
        processed_paper = document_analyzer.process_local_pdf(paper, project_config)
        return f"Successfully processed {processed_paper.title}"
    except Exception as e:
        return f"Error processing {pdf_file}: {str(e)}"


def process_callback(future):
    result = future.result()
    print(result)  # Print result as soon as it's available
    return result


def process_local_pdfs(
    project_config: ProjectConfig,
    local_folder: Annotated[str, "Path to the local folder containing PDFs. Default is './papers'."] = "./papers",
    max_workers: Annotated[int, "Maximum number of worker threads. Default is 4."] = 4
) -> str:
    if not os.path.exists(local_folder):
        return f"Error: The folder {local_folder} does not exist."

    pdf_files = [f for f in os.listdir(local_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        return f"No PDF files found in {local_folder}."

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for pdf_file in pdf_files:
            future = executor.submit(process_single_pdf, pdf_file, local_folder, project_config)
            future.add_done_callback(process_callback)
            futures.append(future)

        # Wait for all futures to complete
        for future in futures:
            results.append(future.result())

    processed_files = [r for r in results if r.startswith("Successfully processed")]
    skipped_files = [r for r in results if r.startswith("Skipping")]
    errors = [r for r in results if r.startswith("Error")]

    result = f"Processed {len(processed_files)} files\n"
    if skipped_files:
        result += f"Skipped {len(skipped_files)} already processed files\n"
    if errors:
        result += f"Encountered {len(errors)} errors\n"

    return result
