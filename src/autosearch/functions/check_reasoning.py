import autogen
from autosearch.agents.utils import termination_msg


def check_reasoning(reason, summary, config_list):
    # Start by instantiating any agent that inherits from ConversableAgent.
    assistant = autogen.AssistantAgent(
        name="reasoning_checker",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
    )

    user = autogen.UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        max_consecutive_auto_reply=0,
        code_execution_config={"use_docker": False},
    )

    chat_hist = user.initiate_chat(assistant, silent=True, message=f"check if \"{reason} is a good reason is to read a paper with the following summary: {summary} /n/n answer only with 'yes' or 'no'")
    return chat_hist.chat_history[-1]['content']
