# File: autosearch/chat/group_chat.py

from typing import List, Dict, Any, Optional
import autogen
from autosearch.agents.base_agent import BaseAgent

class ResearchGroupChat:
    """
    A base class for managing group chats in research-related tasks.
    This class handles the initialization of the group chat, message management,
    and provides methods for initiating and managing conversations.
    """

    def __init__(self, agents: List[BaseAgent], manager_config: Dict[str, Any]):
        """
        Initialize the ResearchGroupChat.

        Args:
            agents (List[BaseAgent]): List of agents participating in the group chat.
            manager_config (Dict[str, Any]): Configuration for the GroupChatManager.
        """
        self.agents = agents
        self.groupchat = autogen.GroupChat(agents=agents, messages=[])
        self.manager = autogen.GroupChatManager(groupchat=self.groupchat, **manager_config)

    def initiate_chat(self, message: str, sender: Optional[BaseAgent] = None) -> List[Dict[str, Any]]:
        """
        Initiate the group chat with a message.

        Args:
            message (str): The message to start the chat with.
            sender (Optional[BaseAgent]): The agent sending the initial message. 
                                          If None, the first agent in the list is used.

        Returns:
            List[Dict[str, Any]]: The chat history.
        """
        if sender is None:
            sender = self.agents[0]

        self.manager.reset()
        sender.initiate_chat(self.manager, message=message, silent=True)
        return self.groupchat.messages

    def add_message(self, message: str, sender: BaseAgent) -> None:
        """
        Add a message to the group chat.

        Args:
            message (str): The message to add.
            sender (BaseAgent): The agent sending the message.
        """
        self.groupchat.messages.append({
            "role": "user" if isinstance(sender, autogen.UserProxyAgent) else "assistant",
            "content": message,
            "name": sender.name
        })

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get the current chat history.

        Returns:
            List[Dict[str, Any]]: The chat history.
        """
        return self.groupchat.messages

    def clear_chat_history(self) -> None:
        """
        Clear the chat history.
        """
        self.groupchat.messages.clear()

    def run_chat(self, max_rounds: int = 10) -> List[Dict[str, Any]]:
        """
        Run the group chat for a specified number of rounds or until termination.

        Args:
            max_rounds (int): Maximum number of chat rounds. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: The final chat history.
        """
        for _ in range(max_rounds):
            if self.manager.is_termination_msg(self.groupchat.messages[-1]):
                break
            self.manager.step()

        return self.get_chat_history()

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """
        Get the last message in the chat history.

        Returns:
            Optional[Dict[str, Any]]: The last message, or None if the chat is empty.
        """
        if self.groupchat.messages:
            return self.groupchat.messages[-1]
        return None

# Usage example
def create_research_group_chat(agents: List[BaseAgent], config: Dict[str, Any]) -> ResearchGroupChat:
    """
    Create a ResearchGroupChat instance.

    Args:
        agents (List[BaseAgent]): List of agents to participate in the group chat.
        config (Dict[str, Any]): Configuration for the group chat manager.

    Returns:
        ResearchGroupChat: An instance of ResearchGroupChat.
    """
    return ResearchGroupChat(agents=agents, manager_config=config)

# Example configuration and usage
if __name__ == "__main__":
    from autosearch.agents.teachable_agent import TeachableAgent

    # Sample configuration
    config = {
        'llm_config': {
            'config_list': [{'model': 'gpt-4'}],
            'temperature': 0.7,
        },
        'is_termination_msg': lambda x: 'TERMINATE' in x.get('content', '').upper()
    }

    # Create sample agents
    agent1 = TeachableAgent("Agent1", "You are a helpful assistant.", config['llm_config'], {})
    agent2 = TeachableAgent("Agent2", "You are a critical thinker.", config['llm_config'], {})

    # Create the group chat
    group_chat = create_research_group_chat([agent1, agent2], config)

    # Initiate and run a chat
    initial_message = "Let's discuss the latest advancements in AI research."
    group_chat.initiate_chat(initial_message, sender=agent1)
    chat_history = group_chat.run_chat(max_rounds=5)

    # Print the chat history
    for message in chat_history:
        print(f"{message['name']}: {message['content']}")