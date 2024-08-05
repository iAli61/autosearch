from typing import Dict, Any
from autosearch.agents.teachable_agent import TeachableAgent

class EditorAgent(TeachableAgent):
    """
    An agent specialized in editing and structuring content.
    """

    def __init__(self, name: str, llm_config: Dict[str, Any], teach_config: Dict[str, Any]):
        system_message = """
        You are a skilled editor responsible for creating well-structured outlines for research articles.
        Your task is to analyze topics, create coherent structures, and ensure that the outline covers
        all necessary aspects of the subject matter.
        """
        super().__init__(name=name, system_message=system_message, llm_config=llm_config, teach_config=teach_config)
