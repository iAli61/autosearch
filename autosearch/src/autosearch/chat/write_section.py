from autosearch.chat.group_chat import ResearchGroupChat
from typing_extensions import Annotated
import os
import autogen

prompt_section = """Compose a blog section with the following guidelines:
Title: {title},
Brief: {brief}

Please ensure your writing aligns closely with the brief provided, capturing the essence of the topic while engaging the reader.
The section should be coherent, well-structured, and reflective of the main themes outlined in the brief.
The section should be include at least one graph that visually help reader to understand the content better.
"""

manager_config = {}


def speaker_selection_func(last_speaker: autogen.Agent, groupchat: autogen.GroupChat):

    data_research_writer = groupchat.agent_by_name("data_research_writer")
    content_review_specialist = groupchat.agent_by_name("content_review_specialist")
    image_developer = groupchat.agent_by_name("image_developer")
    messages = groupchat.messages

    if len(messages) <= 1:
        return data_research_writer

    if all('TXT:' not in mes['content'] for mes in messages) and 'tool_calls' not in messages[-1]:
        return data_research_writer

    if 'TXT:' in messages[-1]['content']:
        return content_review_specialist

    if all('```graphviz ' not in mes['content'] for mes in messages) and 'tool_calls' not in messages[-1]:
        return image_developer

    if '```graphviz ' in messages[-1]['content']:
        return content_review_specialist

    return 'auto'


class SectionWriter(ResearchGroupChat):
    """
    A specialized group chat for creating research article outlines.
    """

    def __init__(self,
                 project_config,
                 agents,
                 max_round=20
                 ):

        super().__init__(
            project_config=project_config,
            agents=agents,
            manager_config=manager_config,
            custom_speaker_selection_func=speaker_selection_func,
            max_round=max_round
        )

    def run(
        self,
        title: Annotated[str, "The title of the section."],
        brief: Annotated[str, "a clear, detailed brief about what section should be included."],
        silent: Annotated[bool, "it should be always True."] = True
    ) -> str:

        chat_hist = self.agents_list[-1].initiate_chat(
            self.manager,
            silent=silent,
            message=prompt_section.format(title=title, brief=brief)
        )
        return self._parse_outline(chat_hist, title, brief)

    def _parse_outline(self, chat_hist, title, brief):
        """
        Parse the outline text into a structured format.
        """

        writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]

        graph = [mes for mes in chat_hist.chat_history if 'GRAPH:' in mes['content']]
        graph_output = graph[-1]['content'].replace("GRAPH:", "").replace("END_GRAPH", "") if graph else "No graph from the writer."

        output = writer_messages[-1]['content'].replace("TXT:", "").replace("END_TXT", "") if writer_messages else "No response from the writer."
        output += "```graphviz \n" + graph_output + "```" if graph else "No graph from the writer."

        # write output in f"{Project_dir}/section_{title}.txt"
        result_dir = f'{self.project_config.project_dir}/results/{self.project_config.logging_session_id}'
        os.makedirs(result_dir, exist_ok=True)
        section_file = f"{result_dir}/section_{title}.md"
        with open(section_file, "w") as f:

            f.write(output)

        return output
