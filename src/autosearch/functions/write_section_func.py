from autosearch.functions.base_function import BaseFunction
from autosearch.agents.agents_creator import AgentsCreator
from autosearch.chat.write_section import SectionWriter
from autosearch.project_config import ProjectConfig
import autogen

from typing_extensions import Annotated
import importlib
# from random import randint


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
    agents = AgentsCreator(project_config=project_config,
                           agents_config=agentsconfig,
                           code_execution=False,
                           ).initialize_agents()

    Code_executor = autogen.UserProxyAgent(
        name="Executor",
        system_message="Executor. Execute the code written by the engineer and report the result.",
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 3,
            "work_dir": "paper",
            "use_docker": False,
        },
    )
    agents.append({"Code_executor": Code_executor})
    section_writer = SectionWriter(project_config, agents, max_round=50)
    return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)
