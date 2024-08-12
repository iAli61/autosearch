from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from autogen.formatting_utils import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


def momorized_text(text, metadata, project_config):
    
    db_dir = project_config.db_dir
    config_list = project_config.config_list

    title = f"{metadata['title']} [{metadata['pdf_url']}] updated on {metadata['updated']}"

    paper_reader, reader_user = create_teachable_groupchat("paper_reader", "reader_user", db_dir, config_list, verbosity=0)
    try:
        reader_user.initiate_chat(paper_reader, silent=True,
                                  message=f"MEMORIZE_ARTICLE: The following passage is extracted from an article titled '{title}': \n\n {text}."
                                  )
    except Exception as e:
        print(f"Error: {e}")
        print(colored(f"text: {text}", "red"))


def chunk_pdf(url, metadata, project_config):

    paper_db = project_config.paper_db
    doc_analyzer = project_config.doc_analyzer
    project_dir = project_config.project_dir

    chunked_elements = doc_analyzer.pdf2md_chunck(url)

    # find checked_elemnt that includes "REFERENCES" in the second half of the text

    half_length = len(chunked_elements) // 2
    for i, chunk in enumerate(chunked_elements[half_length:], start=half_length):
        chunk_text_upper = chunk.page_content.upper()
        if re.search(r'\bREFERENCE\b', chunk_text_upper) or re.search(r'\bREFERENCES\b', chunk_text_upper):
            # remove the chunck with '\bREFERENCE\b' from chuncked_elements list
            chunked_elements = chunked_elements[:i]
            break

    with ThreadPoolExecutor() as executor:  # type: ignore
        futures = [executor.submit(momorized_text, chunk.page_content, metadata, project_config) for chunk in chunked_elements if len(chunk.page_content.split()) > 30]
        for future in as_completed(futures):
            future.result()

    paper_data = {'url': url,
                  'local_path': project_dir,
                  'title': metadata['title'],
                  'authors': metadata['authors'],
                  'published_date': metadata['published'],
                  'last_updated_date': metadata['updated'],
                  }
    paper_db.add_paper("read_papers", paper_data)  # Add paper to the database
