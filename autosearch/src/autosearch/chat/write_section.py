from autosearch.chat.group_chat import ResearchGroupChat
from typing_extensions import Annotated
import os
import autogen

prompt_section = """Compose a blog section with the following guidelines:
Title: {title}
Brief: {brief}

Mind Map of the entire blog post:
```
{mind_map}
```

Please ensure your writing aligns closely with the brief provided and fits coherently within the overall structure shown in the mind map. Your section should:
1. Capture the essence of the topic while engaging the reader.
2. Be coherent, well-structured, and reflective of the main themes outlined in the brief.
3. Relate to other sections of the blog post as indicated in the mind map.
4. Include at least one graph that visually helps the reader to understand the content better.
5. Maintain consistency in style and depth with other sections of the blog post.

Remember to consider how your section fits into the broader context of the entire blog post.
"""


def speaker_selection_func(last_speaker: autogen.Agent, groupchat: autogen.GroupChat):
    data_research_writer = groupchat.agent_by_name("data_research_writer")
    content_review_specialist = groupchat.agent_by_name("content_review_specialist")
    image_developer = groupchat.agent_by_name("image_developer")
    coherence_coordinator = groupchat.agent_by_name("coherence_coordinator")
    messages = groupchat.messages

    if len(messages) <= 1:
        return data_research_writer

    if last_speaker == data_research_writer and 'TXT:' in messages[-1]['content']:
        return content_review_specialist

    if last_speaker == content_review_specialist:
        return coherence_coordinator

    if last_speaker == coherence_coordinator and 'COHERENCE_FEEDBACK:' in messages[-1]['content']:
        return image_developer

    if last_speaker == image_developer and 'GRAPH:' in messages[-1]['content']:
        return data_research_writer  # For potential revisions based on feedback

    return 'auto'


class SectionWriter(ResearchGroupChat):
    def __init__(self, project_config, agents, max_round=20):
        manager_config = {
            "system_message": """
            You are the manager overseeing the creation of a section for a blog post. 
            Your role is to ensure that all agents contribute effectively and that the final section 
            is comprehensive, coherent, and aligns with the overall blog structure. 
            Guide the conversation through the following stages:
            1. Initial draft by the data_research_writer
            2. Review and feedback by the content_review_specialist
            3. Coherence check by the coherence_coordinator
            4. Visual creation by the image_developer
            5. Final revisions and approval
            
            Conclude the process when a satisfactory section has been created and all agents have signed off.
            """
        }

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
        brief: Annotated[str, "A clear, detailed brief about what section should be included."],
        mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
        silent: Annotated[bool, "It should be always True."] = True
    ) -> str:
        chat_hist = self.agents_list[-1].initiate_chat(
            self.manager,
            silent=silent,
            message=prompt_section.format(title=title, brief=brief, mind_map=mind_map)
        )
        return self._parse_outline(chat_hist, title, brief)

    def _parse_outline(self, chat_hist, title, brief):
        """
        Parse the outline text into a structured format.
        """
        writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]
        graph = [mes for mes in chat_hist.chat_history if 'GRAPH:' in mes['content']]
        coherence_feedback = [mes for mes in chat_hist.chat_history if 'COHERENCE_FEEDBACK:' in mes['content']]

        output = f"BRIEF: {brief}\n\n# {title}"
        output += writer_messages[-1]['content'].replace("TXT:", "").replace("END_TXT", "") if writer_messages else "No response from the writer."
        graph_output = graph[-1]['content'].replace("GRAPH:", "").replace("END_GRAPH", "") if graph else "No graph from the image developer."
        feedback = coherence_feedback[-1]['content'].replace("COHERENCE_FEEDBACK:", "").replace("END_COHERENCE_FEEDBACK", "") if coherence_feedback else "No coherence feedback provided."

        output += "\n\n## Coherence Feedback\n" + feedback
        output += "\n\n## Visualization\n```graphviz\n" + graph_output + "\n```"

        # Write output to file
        result_dir = f'{self.project_config.project_dir}/results/{self.project_config.logging_session_id}'
        os.makedirs(result_dir, exist_ok=True)
        section_file = f"{result_dir}/section_{title}.md"
        with open(section_file, "w") as f:
            f.write(output)

        return output
