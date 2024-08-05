from typing import Dict, Any, Callable
import autogen

class BaseAgent(autogen.ConversableAgent):
    """
    Base class for all agents in the AutoSearch project.
    Extends autogen.ConversableAgent with additional functionality.
    """

    def __init__(self, name: str, system_message: str, llm_config: Dict[str, Any]):
        """
        Initialize the BaseAgent.

        Args:
            name (str): The name of the agent.
            system_message (str): The system message for the agent.
            llm_config (Dict[str, Any]): Configuration for the language model.
        """
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)

    def equip_function(self, func: Callable, name: str):
        """
        Equip the agent with a function.

        Args:
            func (Callable): The function to equip.
            name (str): The name of the function.
        """
        self.register_function(func=func, name=name)