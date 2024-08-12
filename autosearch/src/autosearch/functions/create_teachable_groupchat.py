import autogen
from autosearch.agents.teachability import Teachability
from autosearch.agents.utils import termination_msg


def create_teachable_groupchat(assitant_name, user_name, db_dir, config_list,
                               verbosity=0):

    # Start by instantiating any agent that inherits from ConversableAgent.
    assistant = autogen.ConversableAgent(
        # The name is flexible, but should not contain spaces to work in group chat.
        name=assitant_name,
        llm_config={"config_list": config_list, "timeout": 120,
                    "cache_seed": None},
    )

    # Instantiate the Teachability capability. Its parameters are all optional.
    teachability = Teachability(
        # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
        verbosity=verbosity,
        reset_db=False,
        path_to_db_dir=db_dir,
        recall_threshold=1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
    )

    # Now add the Teachability capability to the agent.
    teachability.add_to_agent(assistant)

    user = autogen.UserProxyAgent(
        name=user_name,
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        max_consecutive_auto_reply=0,
        code_execution_config={"use_docker": False},
    )

    return assistant, user
