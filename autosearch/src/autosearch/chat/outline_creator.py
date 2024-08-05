from typing import List, Dict, Any
from autosearch.chat.group_chat import ResearchGroupChat
from autosearch.agents.outlinecreator_agents.editor_agent import EditorAgent
from autosearch.agents.outlinecreator_agents.critic_agent import CriticAgent

class OutlineCreator(ResearchGroupChat):
    """
    A specialized group chat for creating research article outlines.
    """

    def __init__(self, agents: List[TeachableAgent], manager_config: Dict[str, Any]):
        super().__init__(agents, manager_config)
        self.editor = next(agent for agent in agents if isinstance(agent, EditorAgent))
        self.critic = next(agent for agent in agents if isinstance(agent, CriticAgent))

    def create_outline(self, topic: str) -> Dict[str, str]:
        """
        Create an outline for the given topic using the editor and critic agents.

        Args:
            topic (str): The research topic to create an outline for.

        Returns:
            Dict[str, str]: A dictionary representing the outline, with section titles as keys and briefs as values.
        """
        # Initiate the chat with a request to create an outline
        initial_message = f"Create a comprehensive outline for a research article on the topic: {topic}"
        chat_history = self.initiate_chat(initial_message)

        # Extract the final outline from the chat history
        final_message = chat_history[-1]['content']
        return self._parse_outline(final_message)

    def _parse_outline(self, outline_text: str) -> Dict[str, str]:
        """
        Parse the outline text into a structured format.

        Args:
            outline_text (str): The raw outline text from the chat.

        Returns:
            Dict[str, str]: A dictionary with section titles as keys and briefs as values.
        """
        # Implementation to parse the outline text
        # This is a placeholder and should be implemented based on the actual format of your outlines
        outline = {}
        # ... parsing logic ...
        return outline
