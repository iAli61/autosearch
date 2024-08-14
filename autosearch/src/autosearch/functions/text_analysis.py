from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from autosearch.project_config import ProjectConfig
from autosearch.data.paper import Paper
from autogen.formatting_utils import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


def momorized_text(text: str, paper: Paper, project_config: ProjectConfig):

    db_dir = project_config.db_dir
    config_list = project_config.config_list

    title = f"{paper.title} [{paper.url}] updated on {paper.last_updated_date or ""}"

    paper_reader, reader_user = create_teachable_groupchat("paper_reader", "reader_user", db_dir, config_list, verbosity=0)
    try:
        reader_user.initiate_chat(paper_reader, silent=True,
                                  message=f"MEMORIZE_ARTICLE: The following passage is extracted from an article titled '{title}': \n\n {text}."
                                  )
    except Exception as e:
        print(f"Error: {e}")
        print(colored(f"text: {text}", "red"))


def chunk_pdf(paper: Paper, project_config: ProjectConfig):

    paper_db = project_config.paper_db
    doc_analyzer = project_config.doc_analyzer

    chunked_elements = doc_analyzer.pdf2md_chunck(paper)

    # find checked_elemnt that includes "REFERENCES" in the second half of the text

    half_length = len(chunked_elements) // 2
    for i, chunk in enumerate(chunked_elements[half_length:], start=half_length):
        chunk_text_upper = chunk.page_content.upper()
        if re.search(r'\bREFERENCE\b', chunk_text_upper) or re.search(r'\bREFERENCES\b', chunk_text_upper):
            # remove the chunck with '\bREFERENCE\b' from chuncked_elements list
            chunked_elements = chunked_elements[:i]
            break

    print(f"Processing {len(chunked_elements)} chunks from {paper.title}...")
    with ThreadPoolExecutor() as executor:  # type: ignore
        futures = [executor.submit(momorized_text, chunk.page_content, paper, project_config) for chunk in chunked_elements if len(chunk.page_content.split()) > 30]
        for future in as_completed(futures):
            future.result()

    paper_db.add_paper("read_papers", paper)  # Add paper to the database
