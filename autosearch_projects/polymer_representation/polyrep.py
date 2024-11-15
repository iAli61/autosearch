#!/usr/bin/env python3


from autosearch.functions.text_analysis import chunk_pdf

from autosearch.database.paper_database import PaperDatabase
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from autosearch.research_project import ResearchProject
from autosearch.write_blog import WriteBlog

import autogen
from typing import List, Dict, Any

# %%
import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Retrieve Azure credentials from environment variables
config={
    'doc_api_key': os.getenv("DOCUMENT_INTELLIGENCE_KEY"),
    'doc_endpoint': os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
}

os.environ["TOKENIZERS_PARALLELISM"] = "True"

# %%
title = "Exploring the Intricacies of Polymer Representation: Unraveling Complexity"

# %%
blog_project = WriteBlog(
    project_id = "polymer_representation",
    version= "0.3",
    config=config,
    # config_file="../OAI_CONFIG_LIST",
    config_file="../OAI_CONFIG_LIST-sweden-505",
    initiate_db= False,
    funcClsList = ["FactualCheck", "GetPDF", "GetPDFs", "UrlCheck", "AcademicRetriever", "AcademicSearch", "WriteSection", "PlotFigure"],
    communiteList = ["instructor_agents", "outline_agents", "write_section_agents"],
    local_papers_dir="./papers",
    title=title,
    target_audience="expert in experimental polymer science and machine learning experts",
    # models = ["gpt-35-turbo", "gpt-35-turbo-16k"],
)
project_config = blog_project.ProjectConfig
print(project_config.logging_session_id)


# %%
blog_project.run()

# %%
final_blog_post, final_post_file = blog_project.compile_final_blog_post(blog_project.ProjectConfig, title)
print(f"Final blog post has been written to: {final_post_file}")

# %%



