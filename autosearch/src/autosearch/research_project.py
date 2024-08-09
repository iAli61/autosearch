from autosearch.agents.teachable_agent import TeachableAgent
from autosearch.chat.outline_creator import OutlineCreator
from autosearch.functions.get_pdfs import get_pdfs, initialize_get_pdfs
from autosearch.functions.get_pdf import get_pdf, initialize_get_pdf
from autosearch.functions.text_analysis import chunk_pdf
from autosearch.functions.url_check import url_check

from autosearch.database.paper_database import PaperDatabase
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from autosearch.api.arxiv_api import ArxivAPI
from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat
from autosearch.chat.section_writer import SectionWriter
from autosearch.chat.blog_compiler import BlogPostCompiler

from autogen import AssistantAgent, ConversableAgent, UserProxyAgent

from typing import Dict, Any, List, Union


class ResearchProject:
    """
    Main class that orchestrates the entire research project.
    """

    def __init__(self, project_id: str, version: str, topic: str, config: Dict[str, Any]):
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
        self.topic = topic
        self.config = config
        self.db = PaperDatabase(self.projet_dir)
        self.arxiv_api = ArxivAPI()
        self.document_analyzer = DocumentAnalyzer(config['doc_api_key'], config['doc_endpoint'], self.projet_dir)
        self.agents = self._initialize_agents()
        self.outline_creator = OutlineCreator(self.agents['outline'], config['manager'])
        self.section_writer = SectionWriter(self.agents['writing'], config['manager'])
        self.blog_compiler = BlogPostCompiler(self.agents['compiling'], config['manager'])

    def _initialize_agents(self) -> Dict[str, List[Any]]:
        """
        Initialize various agents for different tasks.

        Returns:
            Dict[str, List[TeachableAgent]]: A dictionary of agent groups.
        """
        agents = {}
        for group, agent_configs in self.config['agent_configs'].items():
            agents[group] = []
            for agent_config in agent_configs:
                agent = TeachableAgent(**agent_config)
                if 'functions' in agent_config:
                    for func_name, func in agent_config['functions'].items():
                        agent.equip_function(func, func_name)
                agents[group].append(agent)
        return agents

    def run(self) -> str:
        """
        Execute the entire research workflow.

        Returns:
            str: The final blog post.
        """
        outline = self.outline_creator.create_outline(self.topic)
        sections = [self.section_writer.write_section(title, brief) for title, brief in outline]
        blog_post = self.blog_compiler.compile(sections)
        return blog_post
