from autosearch.functions.base_function import BaseFunction
from autosearch.agents.agents_creator import AgentsCreator
from autosearch.project_config import ProjectConfig
import autogen

from typing_extensions import Annotated
import importlib
import os


class PlotFigure(BaseFunction):
    def __init__(self, project_config: ProjectConfig):
        super().__init__(
            name="plot_figure",
            description="Create a plot or figure using Python code based on the given specifications and research data.",
            func=plot_figure,
            project_config=project_config
        )


def plot_figure(
    project_config: ProjectConfig,
    plot_type: Annotated[str, "The type of plot to create (e.g., 'line', 'scatter', 'bar', 'histogram')."],
    data_description: Annotated[str, "A description of the data to be plotted."],
    x_label: Annotated[str, "Label for the x-axis."],
    y_label: Annotated[str, "Label for the y-axis."],
    title: Annotated[str, "Title of the plot."],
    additional_instructions: Annotated[str, "Any additional instructions or requirements for the plot."] = "",
    silent: Annotated[bool, "Whether to run the agents silently."] = False
):
    # Import the agent configurations
    module = importlib.import_module('autosearch.communities.plot_figure_agents')
    agentsconfig = getattr(module, "agentsconfig")

    # Create agents
    agents = AgentsCreator(project_config=project_config,
                           agents_config=agentsconfig,
                           code_execution=True).initialize_agents()

    # Add the executor agent
    executor = autogen.UserProxyAgent(
        name="plot_executor",
        system_message="Executor. Execute the code written by the engineer and report the result.",
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 20,
            "work_dir": "paper",
            "use_docker": False,
        },
    )
    agents.append({"plot_executor": executor})

    # Create a group chat
    groupchat = autogen.GroupChat(
        agents=[agent for agent_dict in agents for agent in agent_dict.values()],
        messages=[],
        max_round=40
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": project_config.config_list})

    # Prepare the task message
    task_message = f"""
    We need to create a {plot_type} plot with the following specifications:
    - Data description: {data_description}
    - X-axis label: {x_label}
    - Y-axis label: {y_label}
    - Title: {title}
    Additional instructions: {additional_instructions}

    Research Scientist, please start by gathering and validating relevant data for this plot. Use the academic_search, academic_retriever, and get_pdf functions as needed. Provide a summary of the data you find and any important insights.

    Plot Engineer, once the Research Scientist has provided the data, please write Python code to generate this plot using Matplotlib or Seaborn. Save the plot as a PNG file in the 'paper' directory.

    Plot Critic, review the plot and provide feedback to ensure it meets all requirements and effectively represents the data.

    Let's collaborate to create an accurate and informative plot based on validated research data.
    """

    # Initiate the group chat
    chat_result = executor.initiate_chat(
        manager,
        message=task_message,
        silent=silent
    )

    # Extract the path of the generated plot from the chat history
    plot_path = None
    for message in reversed(chat_result.chat_history):
        if "plot_executor" in message["name"] and "saved" in message["content"]:
            plot_path = message["content"].split("saved as ")[-1].strip()
            break

    if plot_path and os.path.exists(plot_path):
        return f"Plot successfully created and saved as {plot_path}"
    else:
        return "Failed to create the plot or find the saved image file."
