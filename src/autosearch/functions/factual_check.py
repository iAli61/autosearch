from typing_extensions import Annotated
from typing import Optional
import autogen
from autogen.token_count_utils import get_max_token_limit
from autogen.agentchat.contrib.capabilities import transform_messages, transforms
from autosearch.functions.url_check import url_check
from autosearch.functions.get_pdf import get_pdf
from autosearch.agents.utils import termination_msg
from autosearch.functions.base_function import BaseFunction
from autosearch.project_config import ProjectConfig


class FactualCheck(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="factual_check",
            description="Check the factual accuracy of a given text based on a paper.",
            func=factual_check,
            project_config=project_config
        )


def factual_check(
    project_config: ProjectConfig,
    text: Annotated[str, "The writer text to be factually checked."],
    paper_title: Annotated[str, "The title of the paper to be used for fact checking."],
    paper_url: Annotated[str, "The URL of the paper to be used for fact checking."],
    reason: Annotated[str, "The reason for reading the paper."],
    paper_authors: Annotated[Optional[str], "The authors of the paper to be used for fact checking."] = None,
) -> str:
    config_list = project_config.config_list

    url_check_res, message = url_check(paper_url, paper_title, project_config)
    if not url_check_res:
        return message

    paper_content = get_pdf(paper_url, reason=reason, part='full', project_config=project_config)

    factual_checker_prompt = """
Below, you will find a passage labeled "TEXT" that references a specific paper: '{paper}' alongside its corresponding "PAPER_CONTENT." Your task is to read the "PAPER_CONTENT" and verify the factual accuracy of the "TEXT" as it pertains to the paper.

Once you have assessed the factual accuracy, you MUST provide feedback, begining with 'FEEDBACK:'. Following your assessment, please write a summary of the paper. Begin this summary with 'Summary of {paper}: '

TEXT:
{text}

PAPER_CONTENT:
{paper_content}
"""

    factual_checker = autogen.AssistantAgent(
        name="factual_checker",
        llm_config={"config_list": config_list, "timeout": 120, "cache_seed": None},
        system_message="You are a factual_check AI assistant. You are responsible for verifying the factual accuracy of the text provided in relation to the paper content."
    )

    factual_checker_user = autogen.UserProxyAgent(
        name="factual_checker_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config=False,
    )

    limit = 0
    try:
        for mod in factual_checker.llm_config["config_list"]:  # type: ignore
            if get_max_token_limit(mod['model']) > limit:
                limit = get_max_token_limit(mod['model']) - 1024
                model = mod['model']
        print(f"max token limit: {limit}")
    except (ValueError, TypeError):
        print("Error determining token limit")
        model = None

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
