from typing import Dict, Any
from autosearch.agents.teachable_agent import TeachableAgent

class CriticAgent(TeachableAgent):
    """
    An agent specialized in critiquing and improving content structure and quality.
    """

    def __init__(self, name: str, llm_config: Dict[str, Any], teach_config: Dict[str, Any]):
        system_message = """
        You are a discerning critic with a keen eye for structure, coherence, and comprehensiveness
        in research article outlines. Your role is to evaluate outlines, suggest improvements,
        and ensure that all crucial aspects of the topic are addressed.
        """
        super().__init__(name=name, system_message=system_message, llm_config=llm_config, teach_config=teach_config)
