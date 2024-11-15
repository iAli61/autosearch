from autosearch.database.paper_database import PaperDatabase
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from autosearch.functions.text_analysis import chunk_pdf
from autosearch.agents.agents_creator import AgentsCreator
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.project_config import ProjectConfig
from autosearch.functions.memorization_skill import memorization_skill
from autosearch.functions.process_local_pdfs import ProcessLocalPDFs

from autosearch.functions.base_function import BaseFunction

import autogen
from typing import Dict, Any, List, Optional
import importlib
import os


class ResearchProject:
    """
    Main class that orchestrates the entire research project.
    """

    def __init__(self,
                 project_id: str, version: str,
                 communiteList: List[str], config: Dict[str, Any],
                 config_file: str, initiate_db: bool = False,
                 funcClsList: Optional[List[str]] = None,
                 local_papers_dir: str = "./papers",
                 models: Optional[List[str]] = None
                 ):
        """
        Initialize the ResearchProject.

        Args:
            project_id (str): Identifier for the project.
            version (str): Version of the project.
            topic (str): Research topic.
            config (Dict[str, Any]): Configuration for the project.
        """
        self.project_id = project_id
        self.version = version
        self.project_dir = f"./{project_id}/{version}"
        self.db_dir = f"{self.project_dir}/db"
        self.config = config
        self.config_file = config_file
        self.initiate_db = initiate_db
        self.config_list = autogen.config_list_from_json(
            self.config_file,
            file_location=".",
            filter_dict={
                "model": [model for model in (models if models is not None else ["gpt-4o", "gpt-4", "gpt-4-32k", "gpt-4o-mini"])]
            },
        )
        self.paper_db = PaperDatabase(self.project_dir)
        self.arxiv_api = ArxivAPI()
        self.document_analyzer = DocumentAnalyzer(config['doc_api_key'], config['doc_endpoint'], self.project_dir, chunk_pdf)
        if initiate_db:
            memorization_skill(self.db_dir, self.config_list, verbosity=0)
        # Start logging
        self.logging_session_id = autogen.runtime_logging.start(config={"dbname": f"{self.project_dir}/logs.db"})  # type: ignore
        print(f"Logging session ID: {str(self.logging_session_id)}")
        self.result_dir = f"{self.project_dir}/results/{self.logging_session_id}"
        os.makedirs(self.result_dir, exist_ok=True)
        self.ProjectConfig = ProjectConfig(
            paper_db=self.paper_db,
            doc_analyzer=self.document_analyzer,
            project_dir=self.project_dir,
            db_dir=self.db_dir,
            config_list=self.config_list,
            initiate_db=self.initiate_db,
            logging_session_id=self.logging_session_id
        )
        self.funcClsList = funcClsList
        self.functions = self._initialize_functions()
        self.communiteList = communiteList
        self.agents_groups = self._initialize_agents()
        # Process local PDFs
        self._process_local_pdfs(local_papers_dir)

    def _initialize_functions(self) -> List[BaseFunction]:
        """
        Initialize various functions for different tasks.

        Returns:
            List[BaseFunction]: A list of function instances.
        """
        functions = []
        if self.funcClsList:
            for function_name in self.funcClsList:
                module = importlib.import_module('autosearch.functions')
                function_class = getattr(module, function_name)  # Get the class from the module
                function = function_class(project_config=self.ProjectConfig)
                functions.append(function)

        self.ProjectConfig.functions = functions
        return functions

    def _initialize_agents(self):
        """
        Initialize various agents for different tasks.

        Returns:
            Dict[str, List[TeachableAgent]]: A dictionary of agent groups.
        """
        agents_groups = {}
        for agent_name in self.communiteList:
            module = importlib.import_module(f'autosearch.communities.{agent_name}')
            agentsconfig = getattr(module, "agentsconfig")
            agents_groups[agent_name] = AgentsCreator(self.ProjectConfig, agents_config=agentsconfig).initialize_agents()

        return agents_groups

    def _process_local_pdfs(self, local_papers_dir: str):
        print("Processing local PDFs...")
        process_local_pdfs_function = ProcessLocalPDFs(self.ProjectConfig)
        result = process_local_pdfs_function.func(self.ProjectConfig, local_papers_dir)
        print(result)
