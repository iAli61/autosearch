from azure.core.serialization import AzureJSONEncoder
from langchain.docstore.document import Document
import tablehelper as tb
import json

from typing import Dict, List, Optional, Union, Callable, Literal
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.formatting_utils import colored
from typing_extensions import Annotated
import autogen
from autogen import Agent
from autogen.token_count_utils import count_token, get_max_token_limit
from autogen.agentchat.contrib.capabilities import transform_messages, transforms

from teachability import Teachability
from concurrent.futures import ThreadPoolExecutor, as_completed

import arxiv

import requests

import os
import shutil
import requests
import pickle
import re
from pathlib import Path
import sqlite3

from dotenv import load_dotenv
load_dotenv()

import os

############################ document analyzer ############################


document_intelligence_key=os.getenv("DOCUMENT_INTELLIGENCE_KEY")
document_intelligence_endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

document_analysis_client = DocumentAnalysisClient(
    endpoint=document_intelligence_endpoint,
    credential=AzureKeyCredential(document_intelligence_key),
)

# ############################# Database helper functions #########################

def init_db(Project_dir):
    """
    Initialize the database for storing abstracts and papers.

    Args:
        Project_dir (str): The directory path where the database file will be created.

    Returns:
        None
    """
    conn = sqlite3.connect(f'{Project_dir}/papers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS read_abstracts (
            url TEXT PRIMARY KEY
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS read_papers (
            url TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()


def add_paper_to_db(paper_url, table_name, Project_dir):
    """
    Add a paper URL to the specified table in the database.

    Args:
        paper_url (str): The URL of the paper to be added.
        table_name (str): The name of the table in the database.
        Project_dir (str): The directory where the database is located.

    Returns:
        None
    """
    conn = sqlite3.connect(f'{Project_dir}/papers.db')
    c = conn.cursor()
    c.execute(f"INSERT OR IGNORE INTO {table_name} (url) VALUES (?)", (paper_url,))
    conn.commit()
    conn.close()

def check_paper_in_db(paper_url, table_name, Project_dir):
    conn = sqlite3.connect(f'{Project_dir}/papers.db')
    c = conn.cursor()
    c.execute(f"SELECT url FROM {table_name} WHERE url = ?", (paper_url,))
    result = c.fetchone()
    conn.close()
    return result

# count the papers in the database
def count_papers_in_db(table_name, Project_dir):
    conn = sqlite3.connect(f'{Project_dir}/papers.db')
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = c.fetchone()
    conn.close()
    return result

############################# arxiv helper functions #########################
def _arxiv_search(query, n_results=10):
    sort_by = arxiv.SortCriterion.Relevance
    papers = arxiv.Search(query=query, max_results=n_results, sort_by=sort_by)
    papers = list(arxiv.Client().results(papers))
    return papers

def arxiv_search(query : Annotated[str, "The title of paper to search for in arxiv."]) -> str:
    papers = _arxiv_search(query, n_results=5)
    if len(papers)>0:
        return ''.join([f" \n\n {i+1}. Title: {paper.title} Authors: {', '.join([str(au) for au in paper.authors])} Pulished at {paper.published} URL: {paper.pdf_url}" for i, paper in enumerate(papers)])
    else:
        return "There are no papers found in arxiv for the given query."

def get_paper_id(url):
    if '/pdf/' in url:
        return url.split('/')[-1].replace('.pdf', '')
    if '/abs/' in url:
        return url.split('/')[-1]
    return url

def get_paper_metadata(url):
    
    paper_id = get_paper_id(url)
    
    search_by_id = arxiv.Search(id_list=[paper_id])
    paper = list(arxiv.Client().results(search_by_id))[0]
    title = paper.title
    link = paper._raw['link']
    updated = paper.updated
    summary = paper.summary
    pdf_url = paper.pdf_url
    authors = ', '.join([str(au) for au in paper.authors])

    return title, link, updated, summary, pdf_url, paper_id, authors

def download_pdf(url, save_path):
    """Download a PDF from a given URL."""
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

############################## Document Analyzer helper functions #########################

def write_json_locally(result, output_folder, pdf_file_path):
    """
    Writes the analysis results to a JSON file locally.

    Args:
        result (dict): Analysis results to be saved as JSON.
        output_folder (str): Folder path where the JSON file will be saved.
        pdf_file_path (str): Path to the PDF file being analyzed.

    Returns:
        str: Path to the saved JSON file.
    """

     # Save the result as JSON locally
   
    analyze_result_dict = result
    #write results to json file
    jsonfile = f"{output_folder}/{pdf_file_path}.json"
    with open(jsonfile, 'w', encoding='utf-8') as f:

        json.dump(analyze_result_dict, f, cls=AzureJSONEncoder, ensure_ascii=False, indent=4)
    return jsonfile 

def read_pdf_content(pdf_file_path):
    """
    Reads PDF content from a local or remote path.
    """
    # check if pdf_file_path is starting with file://
    if isinstance(pdf_file_path, str) and pdf_file_path.startswith("file://"):
        local_pdf_path = pdf_file_path.replace("file://", "")
        with open(local_pdf_path, "rb") as local_pdf_file:
            return local_pdf_file.read()
    else:
        download_stream = pdf_file_path.download_file()
        return download_stream.readall()

def _analyze_and_save_pdf(document_analysis_client, pdf_content):
    # Analyze the PDF content
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
    result = poller.result().to_dict()

    print("Writing results to json file...")
    return result

def analyze_and_save_pdf(pdf_file_path, output_folder, file_system_client=None, output_file_system_client=None, output_container_name=None):
    """
    Analyzes a PDF file and saves the results, with simplified handling for reading PDF content.
    """
    file_name = pdf_file_path.split("/")[-1]
    if pdf_file_path.startswith("file://"):
        pdf_content = read_pdf_content(pdf_file_path)
        result = _analyze_and_save_pdf(document_analysis_client, pdf_content)
        write_json_locally(result, output_folder, file_name)
    else:
        file_client = file_system_client.get_file_client(pdf_file_path)
        pdf_content = read_pdf_content(file_client)
        result = _analyze_and_save_pdf(document_analysis_client, pdf_content)
        metadata = file_client.get_file_properties().metadata
        # write_to_adls(file_name, result, output_container_name, output_file_system_client, file_client, metadata)
    
    return result

def create_docs(data, maxtokensize, sourcename1):
    """
    Creates documents from input data, separating content based on section headings and page numbers.

    Args:
        data (dict): Input data containing paragraphs and tables.
        maxtokensize (int): Maximum token size for each document.
        sourcename1 (str): Name of the source.

    Returns:
        tuple: A tuple containing:
            - list: Documents created from the input data.
            - dict: Page content extracted from the input data.
            - str: Full markdown text generated from the input data.
    """

    # Initialize variables
    docs = []  # List to store Document objects
    pagecontent = {}  # Dictionary to store page content
    fullmdtext = ""  # String to store full markdown text
    mdtextlist = []  # List to store markdown text for each paragraph
    pagenr = []  # List to store page numbers
    pagesources = []  # List to store page sources
    sectionHeading = ""  # Variable to store section heading
    largestdoc = 0  # Variable to store the size of the largest document
    endoftable=0
    tablesearchkey=-1
    mdtext =""
    listoftext =[]

    print(" running create_docs")
    spans={}
    #collect spans from tables
    for idx,tab in enumerate(data['tables']):
        if(len(tab['spans'])==1):
            key=tab['spans'][0]['offset']
            spans[str(key)]=idx
        else:
            smallesoffset=9999999999999999999999999
            for sp in tab['spans']:
                if sp['offset']<smallesoffset:
                    smallesoffset=sp['offset']
            spans[str(smallesoffset)]=idx

    #create pagecontent object
    pagecontent={}
    for i in range(1,len(data['pages'])+1):
        pagecontent[str(i)]=""

    # Define a helper function to count the number of tokens in a given text
    def gettokens(text):
        import tiktoken
        enc = tiktoken.encoding_for_model('gpt-3.5-turbo')
        return len(enc.encode(text))

    # Iterate through each paragraph in the data
    #iterate over all paragraphes and create docs with mdtext seperated by sectionHeadings
    for paragraphes in data['paragraphs']:
        #when content is 7 Price conditions, then print content
        if paragraphes['spans'][0]['offset']>=endoftable:
            if 'role' in paragraphes:
                if paragraphes['role']=='sectionHeading':
                    if sectionHeading!=paragraphes['content']:
                        #only create new doc if sectionHeading is not empty
                        if sectionHeading!='':
                            #build mdtext and create docs with content smaller than maxtokensize
                            mdtext = f"## {sectionHeading}" + "\n\n"

                            #add content to pagecontent object
                            key=str(paragraphes['bounding_regions'][0]['page_number'])
                            if key in pagecontent:
                                pagecontent[key] = f"{pagecontent[key]}## " + paragraphes['content'] + "\n\n"
                            else:
                                pagecontent[key]="## "+paragraphes['content']+"\n\n"

                            pagesources = []
                            for pid,md in enumerate(mdtextlist):
                                if gettokens(mdtext+md)<=maxtokensize:
                                    mdtext=mdtext+md
                                    if pagenr[pid] not in pagesources:
                                        pagesources.append(pagenr[pid])
                                else:
                                    if (gettokens(md)>maxtokensize):
                                        tokens=gettokens(md)
                                        if tokens>largestdoc:
                                            largestdoc=tokens
                                        docs.append(Document(page_content=md, metadata={"source": sourcename1, "pages":[pagenr[pid]], "tokens":tokens}))   
                                        fullmdtext=fullmdtext+md
                                    else:         
                                        tokens=gettokens(mdtext)
                                        if tokens>largestdoc:
                                            largestdoc=tokens
                                        docs.append(Document(page_content=mdtext, metadata={"source": sourcename1, "pages":pagesources, "tokens":tokens}))
                                        #add to fullmdtext
                                        fullmdtext=fullmdtext+mdtext
                                        mdtext=md
                                        pagesources = [pagenr[pid]]

                            #add last doc 
                            if len(pagesources)>0:
                                fullmdtext=fullmdtext+mdtext
                                tokens=gettokens(mdtext)
                                if tokens>largestdoc:
                                    largestdoc=tokens
                                docs.append(Document(page_content=mdtext, metadata={"source": sourcename1, "pages":pagesources, "tokens":tokens}))

                            #reset mdtext and pagenr
                            mdtextlist=[]
                            pagenr=[]
                        #set new sectionHeading
                        sectionHeading=paragraphes['content']
                else:
                    #add paragraphes to mdtext
                    mdtextlist.append(paragraphes['content']+"\n\n")
                    page=paragraphes['bounding_regions'][0]['page_number']
                    pagenr.append(page)
                    #add content to pagecontent object
                    key=str(paragraphes['bounding_regions'][0]['page_number'])
                    if key in pagecontent:
                        pagecontent[key]=pagecontent[key]+paragraphes['content']+"\n\n"
                    else:
                        pagecontent[key]=paragraphes['content']+"\n\n"

            else:
                mdtextlist.append(paragraphes['content']+"\n\n")
                page=paragraphes['bounding_regions'][0]['page_number']
                pagenr.append(page)
                #add content to pagecontent object
                key=str(paragraphes['bounding_regions'][0]['page_number'])
                if key in pagecontent:
                    pagecontent[key]=pagecontent[key]+paragraphes['content']+"\n\n"
                else:
                    pagecontent[key]=paragraphes['content']+"\n\n"

            #add pagenr if not already in list
            page=paragraphes['bounding_regions'][0]['page_number']
            pagenr.append(page)

        #add subsequent table if exists
        searchkey=str(paragraphes['spans'][0]['offset']+paragraphes['spans'][0]['length']+1)
        if tablesearchkey in spans or searchkey in spans:
            i=spans[searchkey]
            mdtextlist.append("\n\n"+tb.tabletomd(data['tables'][i])+"\n\n")
            #add content to pagecontent object
            key=str(paragraphes['bounding_regions'][0]['page_number'])
            if key in pagecontent:
                pagecontent[key]=pagecontent[key]+"\n\n"+tb.tabletomd(data['tables'][i])+"\n\n"
            else:
                pagecontent[key]="\n\n"+tb.tabletomd(data['tables'][i])+"\n\n"

            if len(data['tables'][i]['spans'])>1:
                smallesoffset=9999999999999999999999999
                totallength=0
                for sp in data['tables'][i]['spans']:
                    totallength=totallength+sp['length']
                    if sp['offset']<smallesoffset:
                        key=sp['offset']
                        smallesoffset=sp['offset']
                endoftable=smallesoffset+totallength+1
                tablesearchkey=smallesoffset+totallength+1
            else:
                endoftable=data['tables'][i]['spans'][0]['offset']+data['tables'][i]['spans'][0]['length']+1
                tablesearchkey=data['tables'][i]['spans'][0]['offset']+data['tables'][i]['spans'][0]['length']+1
            page=data['tables'][i]['bounding_regions'][0]['page_number']
            pagenr.append(page)
    key=str(paragraphes['bounding_regions'][0]['page_number'])
    listoftext.append(pagecontent[key])
    for pid,md in enumerate(mdtextlist):
        if gettokens(mdtext+md)<=maxtokensize:
            mdtext=mdtext+md
            if pagenr[pid] not in pagesources:
                pagesources.append(pagenr[pid])
        else:
            if (gettokens(md)>maxtokensize):
                tokens=gettokens(md)
                if tokens>largestdoc:
                    largestdoc=tokens
                docs.append(Document(page_content=md, metadata={"source": sourcename1, "pages":[pagenr[pid]], "tokens":tokens}))   
                fullmdtext=fullmdtext+md
            else:
                tokens=gettokens(mdtext)
                if tokens>largestdoc:
                    largestdoc=tokens
                docs.append(Document(page_content=mdtext, metadata={"source": sourcename1, "pages":pagesources, "tokens":tokens}))
                #add to fullmdtext
                fullmdtext=fullmdtext+mdtext
                mdtext=md
                pagesources = [pagenr[pid]]

    #add last doc 
    if len(pagesources)>0:
        #add to fullmdtext
        fullmdtext=fullmdtext+mdtext
        docs.append(Document(page_content=mdtext, metadata={"source": sourcename1, "pages":pagesources, "tokens":gettokens(mdtext)}))


    print(
        (
            (
                (
                    f"Created {len(docs)} docs with a total of "
                    + str(gettokens(fullmdtext))
                )
                + " tokens. Largest doc has "
            )
            + str(largestdoc)
            + " tokens."
        )
    )
    return docs, pagecontent,fullmdtext


############################## 

def pdf2md_chunck(url):
    if url[-4:] != ".pdf":
        pdf_filename = url.split('/')[-1] + ".pdf"
    else:
        pdf_filename = url.split('/')[-1]

    if url.startswith("http"):
        pdf_path = os.path.join(output_dir, pdf_filename)
        # Download the PDF
        download_pdf(url, pdf_path)
    else:
        pdf_path = url

    data = analyze_and_save_pdf(f"file://{pdf_path}", f"{output_dir}/json")

    docs, pagecontent, fullmdtext = create_docs(data, 3000, pdf_filename)

    # write fullmdtext to a file
    with open(f"{output_dir}/markdown/{pdf_filename}.md", "w") as f:
        f.write(fullmdtext)

    return docs
