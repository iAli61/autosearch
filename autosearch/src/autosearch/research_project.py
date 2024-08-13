from autosearch.database.paper_database import PaperDatabase
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from autosearch.agents.agents_creator import AgentsCreator
from autosearch.chat.outline_creator import OutlineCreator
from autosearch.chat.instruction_creator import InstructionCreator
from autosearch.chat.write_section import SectionWriter
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.project_config import ProjectConfig
from autosearch.functions.memorization_skill import memorization_skill
from autosearch.functions.process_local_pdfs import ProcessLocalPDFs

from autosearch.functions.base_function import BaseFunction

import autogen
from typing import Dict, Any, List, Optional
import importlib
from typing_extensions import Annotated
import os
import re


class ResearchProject:
    """
    Main class that orchestrates the entire research project.
    """

    def __init__(self,
                 project_id: str, version: str,
                 communiteList: List[str], config: Dict[str, Any],
                 config_file: str, initiate_db: bool = False,
                 funcClsList: Optional[List[str]] = None,
                 local_papers_dir: str = "./papers"
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
        self.projet_dir = f"./{project_id}/{version}"
        self.db_dir = f"{self.projet_dir}/db"
        self.config = config
        self.config_file = config_file
        self.initiate_db = initiate_db
        self.config_list = autogen.config_list_from_json(
            self.config_file,
            file_location=".",
            filter_dict={
                "model": ["gpt-4o", "gpt-4", "gpt-4-32k", "gpt-4o-mini"],
            },
        )
        self.paper_db = PaperDatabase(self.projet_dir)
        self.arxiv_api = ArxivAPI()
        self.document_analyzer = DocumentAnalyzer(config['doc_api_key'], config['doc_endpoint'], self.projet_dir)
        if initiate_db:
            memorization_skill(self.db_dir, self.config_list, verbosity=0)
        # Start logging
        self.logging_session_id = autogen.runtime_logging.start(config={"dbname": f"{self.project_id}/logs.db"})  # type: ignore
        print(f"Logging session ID: {str(self.logging_session_id)}")
        self.result_dir = f"{self.projet_dir}/results/{self.logging_session_id}"
        os.makedirs(self.result_dir, exist_ok=True)
        self.ProjectConfig = ProjectConfig(
            paper_db=self.paper_db,
            doc_analyzer=self.document_analyzer,
            project_dir=self.projet_dir,
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
        process_local_pdfs_function = ProcessLocalPDFs(self.ProjectConfig)
        result = process_local_pdfs_function.func(self.ProjectConfig, local_papers_dir)
        print(result)

    def run(self, title: str, target_audience: str):
        """
        Execute the entire research workflow.

        Args:
            title (str): The title of the article.
            target_audience (str): The target audience for the article.

        Returns:
            str: The final blog post.
        """
        self.title = title
        self.target_audience = target_audience

        # Create instruction
        self.instruction_creator = InstructionCreator(self.ProjectConfig, self.agents_groups['instructor_agents'])
        self.instruction = self.instruction_creator.run(title, target_audience, silent=False)
        # Create outline
        self.outline_creator = OutlineCreator(self.ProjectConfig, self.agents_groups['outline_agents'], max_round=150)

        def write_section(
                title: Annotated[str, "The title of the section."],
                brief: Annotated[str, "A clear, detailed brief about what the section should include."],
                mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
                silent: Annotated[bool, "It should always be True."] = True
        ):
            module = importlib.import_module('autosearch.communities.write_section_agents')
            agentsconfig = getattr(module, "agentsconfig")
            agents = AgentsCreator(self.ProjectConfig, agents_config=agentsconfig).initialize_agents()
            section_writer = SectionWriter(self.ProjectConfig, agents, max_round=20)
            return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)

        # find blog_editor agent in self.agents_groups['outline_agents']
        agents_dict = {k: v for d in self.agents_groups['outline_agents'] for k, v in d.items()}
        blog_editor = agents_dict.get("blog_editor-in-chief", None)
        if blog_editor is None:
            raise ValueError("No blog_editor-in-chief agent found in outline_agents")
        autogen.agentchat.register_function(
            f=write_section,
            name="write_section",
            caller=blog_editor,
            executor=agents_dict['editor_user'],
            description="Write a section based on the given title, brief, and mind map.",
        )

        mind_map, titles, briefs, overall_word_count = self.outline_creator.run(
            title=self.title,
            instruction=self.instruction,
            silent=False,
        )

        # sections = []
        # with ThreadPoolExecutor() as executor:
        #     futures = [executor.submit(write_section, title=title, brief=brief) for title, brief in zip(titles, briefs)]
        #     for future in futures:
        #         sections.append(future.result())

        #     return self.postprocessing(sections)

    def postprocessing(self, sections):
        """
        Perform post-processing on the sections.

        Args:
            sections (List[str]): List of sections.

        Returns:
            Tuple[List[str], List[str]]: Tuple containing the processed section text and section references.
        """
        section_text = []
        section_refs = []
        for secs in sections:
            # split section based on "References" or "Citations" and "graphviz"
            if len(secs.split("References:")) > 1:
                section_text.append(secs.split("References:")[0].strip())
                remaining_text = secs.split("References:")[1]
                if len(remaining_text.split("```graphviz")) > 1:
                    section_refs.append(remaining_text.split("```graphviz")[0].strip())
                    section_text.append(remaining_text.split("```graphviz")[1].strip())
                else:
                    print(f"the following sections does not have graphviz: {secs}")
                    section_refs.append(remaining_text.strip())
            elif len(secs.split("Citations:")) > 1:
                section_text.append(secs.split("Citations:")[0].strip())
                remaining_text = secs.split("Citations:")[1]
                if len(remaining_text.split("```graphviz")) > 1:
                    section_refs.append(remaining_text.split("```graphviz")[0].strip())
                    section_text.append(remaining_text.split("```graphviz")[1].strip())
                else:
                    print(f"the following sections does not have graphviz: {secs}")
                    section_refs.append(remaining_text.strip())
            else:
                print(f"the following sections does not have Citations: {secs}")

        blog_sections = f"# {self.title}\n\n"
        blog_sections += "\n\n".join(f'## {i}. {section}' for i, section in enumerate(section_text, start=1))
        blog_sections += "Citations: \n"
        blog_sections += '\n'.join(section_refs)

        # remove "TXT", "TERMINATE", "END_TXT" from the blog_sections
        blog_sections = f"""{re.sub(r'TXT:|TERMINATE|END_TXT:|TXT|END_TXT', '', blog_sections)}"""

        blog_sections = blog_sections.strip()
        # print(blog_sections)

        with open(f'{self.result_dir}/blog_post-{self.logging_session_id}.md', 'w') as f:
            f.write(blog_sections)

        # read blog_sections
        with open(f'{self.result_dir}/blog_post-{self.logging_session_id}.md', 'r') as f:
            blog_sections = f.read()

        return blog_sections
