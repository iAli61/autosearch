from typing import List, Dict, Any, Callable, Union
import autogen
from autosearch.project_config import ProjectConfig
from autosearch.agents.utils import termination_msg


class ResearchGroupChat:
    """
    A base class for managing group chats in research-related tasks.
    This class handles the initialization of the group chat, message management,
    and provides methods for initiating and managing conversations.
    """

    def __init__(self,
                 project_config: ProjectConfig,
                 agents: List[Dict[str, autogen.ConversableAgent]],
                 manager_config: Dict[str, Any],
                 custom_speaker_selection_func: Union[Callable, str] = "auto",
                 max_round: int = 10
                 ):
        """
        Initialize the ResearchGroupChat.

        Args:
            agents (List[BaseAgent]): List of agents participating in the group chat.
            manager_config (Dict[str, Any]): Configuration for the GroupChatManager.
        """
        self.project_config = project_config
        self.llm_config = {
            "config_list": project_config.config_list,
            "timeout": 60,
            # "seed": 42,
        }
        self.manager_config = manager_config
        self.agents = agents
        self.custom_speaker_selection_func = custom_speaker_selection_func
        self.agents_list = [agent for agent_dict in self.agents for agent in agent_dict.values()]
        self.groupchat = autogen.GroupChat(
            agents=[agent for agent_dict in self.agents for agent in agent_dict.values()],
            messages=[],
            speaker_selection_method=custom_speaker_selection_func,  # type: ignore
            allow_repeat_speaker=True,
            max_round=max_round,
        )
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            is_termination_msg=termination_msg,
            llm_config=self.llm_config,
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,
            },
            **manager_config
        )

    def initiate_chat(self, message: str, messages: List[str] = [], silent: bool = False):
        """
        Initiate the group chat with a message.
        """
        return self.agents_list[-1].initiate_chat(self.manager, silent=silent, message=message, messages=messages)

    def run(self, message: str, messages: List[str] = [], silent: bool = False):
        """
        this should be implemented in the child class
        """
        pass

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get the current chat history.
        """
        return self.groupchat.messages

    def clear_chat_history(self) -> None:
        """
        Clear the chat history.
        """
        self.groupchat.messages.clear()

    def get_last_message(self):
        """
        Get the last message in the chat history.
        """
        if self.groupchat.messages:
            return self.groupchat.messages[-1]
        return None
