from typing_extensions import Annotated
from autosearch.functions.url_check import url_check
from autosearch.functions.get_pdf import get_pdf_with_config
from autosearch.agents.base_agent import termination_msg

import autogen
from autogen.token_count_utils import get_max_token_limit
from autogen.agentchat.contrib.capabilities import transform_messages, transforms
from typing import List, Dict, Any, Optional


# Global configuration object
global_config: Dict[str, Any] = {}


def initialize_factual_check(
    paper_db,
    doc_analyzer,
    project_dir: str,
    db_dir: str,
    config_list: List[dict],
    initiate_db: bool = False,
    **kwargs
):
    """Initialize the global configuration object."""
    global global_config
    global_config = {
        "paper_db": paper_db,
        "doc_analyzer": doc_analyzer,
        "project_dir": project_dir,
        "db_dir": db_dir,
        "config_list": config_list,
        "initiate_db": initiate_db
    }


def factual_check(text: Annotated[str, "The writer text to be factually checked."],
                  paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
                  paper_url: Annotated[str, "The arxiv URL of the paper to be used for fact checking."],
                  reason: Annotated[str, "The reason for reading the paper."],
                  paper_authors: Annotated[Optional[str], "The authors of the paper to be used for fact checking."] = None,
                  ) -> str:

    global global_config
    if not global_config:
        raise ValueError("Global configuration not initialized. Call initialize_global_config first.")

    config_list = global_config["config_list"]

    url_check_res, message = url_check(paper_url, paper_title)
    if not url_check_res:
        return message

    paper_content = get_pdf_with_config(paper_url, reason=reason, part='full', config=global_config)

    factual_checker_prompt = """
Below, you will find a passage labeled "TEXT" that references a specific paper: '{paper}' alongside its corresponding "PAPER_CONTENT." Your task is to read the "PAPER_CONTENT" and verify the factual accuracy of the "TEXT" as it pertains to the paper.

Once you have assessed the factual accuracy, you MUST provide feedback, begining with 'FEEDBACK:'. Following your assessment, please write a summary of the paper. Begin this summary with 'Summary of {paper}: '

TEXT:
{text}

PAPER_CONTENT:
{paper_content}
"""

    # Start by instantiating any agent that inherits from ConversableAgent.
    factual_checker = autogen.AssistantAgent(
        name="factual_checker",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},  # Disable caching.
        system_message="You are a factual_check AI assistant. You are responsible for verifying the factual accuracy of the text provided in relation to the paper content."
    )

    # create a UserProxyAgent instance named "user_proxy"
    factual_checker_user = autogen.UserProxyAgent(
        name="factual_checker_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config=False,
    )

    # let check token limit
    limit = 0
    try:
        # find the model in the config_list that has longest token limit
        for mod in factual_checker.llm_config["config_list"]:  # type: ignore
            if get_max_token_limit(mod['model']) > limit:
                limit = get_max_token_limit(mod['model']) - 1024  # reserve 1024 tokens for the agent
                model = mod['model']

        print(f"max token limit: {limit}")
    except ValueError:
        print("ValueError")
        pass  # limit is unknown
    except TypeError:
        print("TypeError")
        pass  # limit is unknown

    # Limit the token limit per message to avoid exceeding the maximum token limit
    # suppose this capability is not available
    context_handling = transform_messages.TransformMessages(
        transforms=[
            transforms.MessageTokenLimiter(max_tokens=limit, model=model),  # type: ignore
        ]
    )
    print(f"factual_check model: {model}")  # type: ignore
    context_handling.add_to_agent(factual_checker)

    if paper_authors:
        paper = f"{paper_title} [{paper_url}] by {', '.join(list(paper_authors.split(',')))}"
    else:
        paper = f"{paper_title} [{paper_url}]"

    chat = factual_checker_user.initiate_chat(factual_checker, silent=False, max_turns=1,
                                              message=factual_checker_prompt.format(text=text, paper_content=paper_content, paper=paper))

    return chat.chat_history[-1]['content']
