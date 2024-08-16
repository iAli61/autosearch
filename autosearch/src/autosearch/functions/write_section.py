from autosearch.functions.base_function import BaseFunction
from autosearch.agents.agents_creator import AgentsCreator
from autosearch.chat.write_section import SectionWriter
from autosearch.project_config import ProjectConfig

from typing_extensions import Annotated
import importlib
from random import randint


class WriteSection(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="write_section",
            description="Retrieve the content of the pdf file from the url.",
            func=write_section,
            project_config=project_config
        )


def write_section(
    project_config: ProjectConfig,
    title: Annotated[str, "The title of the section."],
    brief: Annotated[str, "A clear, detailed brief about what the section should include."],
    mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
    silent: Annotated[bool, "It should always be True."] = True
):
    module = importlib.import_module('autosearch.communities.write_section_agents')
    agentsconfig = getattr(module, "agentsconfig")
    prefix = f"section_{randint(0, 1000)}"
    agents = AgentsCreator(project_config=project_config,
                           agents_config=agentsconfig,
                           prefix=prefix
                           ).initialize_agents()
    section_writer = SectionWriter(project_config, agents, max_round=50)
    return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)