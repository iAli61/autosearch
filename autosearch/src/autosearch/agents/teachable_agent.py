from autosearch.agents.base_agent import BaseAgent
from autosearch.agents.teachability import Teachability

class TeachableAgent(BaseAgent):
    """
    An agent equipped with the Teachability capability.
    """

    def __init__(self, name: str, system_message: str, llm_config: Dict[str, Any], 
                 teach_config: Dict[str, Any]):
        """
        Initialize the TeachableAgent.

        Args:
            name (str): The name of the agent.
            system_message (str): The system message for the agent.
            llm_config (Dict[str, Any]): Configuration for the language model.
            teach_config (Dict[str, Any]): Configuration for the Teachability capability.
        """
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)
        self.teachability = Teachability(**teach_config)
        self.teachability.add_to_agent(self)