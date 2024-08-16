import random
import autogen
from dataclasses import dataclass
from typing import List, Optional, Union

from autosearch.agents.teachability import Teachability
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig


@dataclass
class TeachabilityConfig:
    db_dir: Optional[str] = None
    verbosity: int = 0
    reset_db: bool = False
    recall_threshold: float = 1.5


@dataclass
class AgentConfig:
    name: str
    system_message: str
    description: str
    function_list: Optional[List[BaseFunction]] = None
    teachable: Optional[TeachabilityConfig] = None
    learnable: Optional[bool] = True


class BaseAgent(autogen.AssistantAgent):
    """
    Base class for all agents in the AutoSearch project.
    Extends autogen.AssistantAgent with additional functionality.
    """

    def __init__(self,
                 agent_config: AgentConfig,
                 project_config: ProjectConfig,
                 executor: Union[autogen.ConversableAgent, None] = None,
                 prefix: Optional[str] = None,
                 **kwargs
                 ):
        """
        Initialize the BaseAgent.

        Args:
            name (str): The name of the agent.
            system_message (str): The system message for the agent.
            llm_config (Dict[str, Any]): Configuration for the language model.
        """
        self.agent_config = agent_config
        self.project_config = project_config
        self.llm_config = {
            "config_list": self.project_config.config_list,
            "timeout": 120,
            # "seed": 42,
        }
        if prefix:
            _name = f"{prefix}_{agent_config.name}"
        else:
            _name = agent_config.name
        super().__init__(
            name=_name,
            system_message=agent_config.system_message,
            description=agent_config.description,
            llm_config=self.llm_config
        )

        if self.agent_config.teachable:
            teachability = Teachability(
                verbosity=int(getattr(self.agent_config.teachable, 'verbosity', getattr(self.project_config, 'verbosity', 0))),
                reset_db=getattr(self.agent_config.teachable, 'reset_db', getattr(self.project_config, 'reset_db', False)),
                path_to_db_dir=getattr(self.agent_config.teachable, 'db_dir', getattr(self.project_config, 'db_dir', self.project_config.project_dir + '/db')),
                recall_threshold=getattr(self.agent_config.teachable, 'recall_threshold', getattr(self.project_config, 'recall_threshold', 1.5)),
                learnable=getattr(self.agent_config.teachable, 'learnable', True)
            )
            teachability.add_to_agent(self)

        if self.agent_config.function_list:
            # check if there is executor for this agnet
            if executor is None:
                raise ValueError("Executor is required to equip functions.")

            functions_list = [func.name for func in self.project_config.functions] if self.project_config.functions else []
            for func_name in self.agent_config.function_list:
                if func_name not in functions_list:
                    raise ValueError(f"Function '{func_name}' not found in the project functions.")
            for func_name in self.agent_config.function_list:
                for func in self.project_config.functions:  # type: ignore
                    if func.name == func_name:
                        print(f"Equipping function '{func.name}' to agent '{self.name}'")
                        self.equip_function(func=func, executor=executor)

    def equip_function(self, func: BaseFunction, executor: autogen.ConversableAgent):
        """
        Equip the agent with a function.

        Args:
            func (Callable): The function to equip
        """

        autogen.agentchat.register_function(
            f=func.func,
            name=func.name + f"_{self.name}_{random.randint(0, 100000)}",
            caller=self,
            executor=executor,
            description=func.description
        )
