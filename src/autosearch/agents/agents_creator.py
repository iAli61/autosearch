from autosearch.agents.base_agent import AgentConfig, BaseAgent
from autosearch.agents.utils import termination_msg
from autosearch.project_config import ProjectConfig
from typing import List, Optional
import autogen


class AgentsCreator:

    def __init__(self,
                 project_config: ProjectConfig,
                 agents_config: List[AgentConfig],
                 prefix: Optional[str] = None,
                 code_execution: bool = False
                 ):
        self.project_config = project_config
        self.llm_config = {
            "config_list": self.project_config.config_list,
            "timeout": 120,
        },
        self.agents_config = agents_config
        self.prefix = prefix
        self.code_execution = code_execution

    def initialize_agents(self):

        # create a UserProxyAgent instance named "user_proxy"
        if self.code_execution:
            executor = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                is_termination_msg=termination_msg,
                code_execution_config={
                    "work_dir": self.project_config.project_dir,
                    "use_docker": False
                },
            )
        else:
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
                executor=executor,
                prefix=self.prefix,
            )
            agents.append({agent.name: agent})

        return agents + [{executor.name: executor}]
