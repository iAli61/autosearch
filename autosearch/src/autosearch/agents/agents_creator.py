from autosearch.agents.base_agent import AgentConfig, BaseAgent
from autosearch.agents.utils import termination_msg
from autosearch.project_config import ProjectConfig
from typing import List
import autogen


class AgentsCreator:

    def __init__(self,
                 project_config: ProjectConfig,
                 agents_config: List[AgentConfig]
                 ):
        self.project_config = project_config
        self.llm_config = {
            "config_list": self.project_config.config_list,
            "timeout": 120,
        },
        self.agents_config = agents_config

    def initialize_agents(self):

        # create a UserProxyAgent instance named "user_proxy"
        executor = autogen.UserProxyAgent(
            name="editor_user",
            human_input_mode="NEVER",
            is_termination_msg=termination_msg,
            code_execution_config=False,
        )

        # create a list of agents based on the provided configuration
        agents = []
        for agent_config in self.agents_config:
            agent = BaseAgent(
                agent_config=agent_config,
                project_config=self.project_config,
                executor=executor
            )
            agents.append({agent.name: agent})

        return agents + [{executor.name: executor}]
