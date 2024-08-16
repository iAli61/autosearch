from autosearch.chat.group_chat import ResearchGroupChat
import autogen
import re
import os


def speaker_selection_func(last_speaker: autogen.Agent, groupchat: autogen.GroupChat):

    blog_editor = groupchat.agent_by_name("blog_editor-in-chief")
    critic = groupchat.agent_by_name("content_strategist")
    messages = groupchat.messages
    # speakers = [m['name'] for m in messages]
    if len(messages) <= 1:
        return blog_editor

    if all('OUTLINE' not in mes['content'] for mes in messages) and 'tool_calls' not in messages[-1]:
        return blog_editor

    if 'OUTLINE' in messages[-1]['content']:
        return critic

    if last_speaker == critic and messages[-1]["content"] == "FEEDBACK:":
        return blog_editor

    return 'auto'


manager_system_message = """
You are the manager of the group chat. Your role is to oversee the collaborative creation of a blog post.
Ensure that the blog editor and critic work together effectively to craft a well-structured, data-driven post.
When you receive a message from the blog editor with the keyword 'OUTLINE,' promptly assign the critic to review the outline provided. If no such message is received, allow the blog editor to proceed with content creation.
Monitor the progress, provide guidance, and address any issues that arise during the project.
"""

manager_config = {
    "system_message": manager_system_message,
}


class OutlineCreator(ResearchGroupChat):
    """
    A specialized group chat for creating research article outlines.
    """

    def __init__(self,
                 project_config,
                 agents,
                 max_round=10
                 ):

        super().__init__(
            project_config=project_config,
            agents=agents,
            manager_config=manager_config,
            custom_speaker_selection_func=speaker_selection_func,
            max_round=max_round
        )

    def run(self, title, instruction, silent):
        self.title = title
        self.instruction = instruction
        chat_hist = self.agents_list[-1].initiate_chat(
            self.manager,
            silent=silent,
            message=instruction.format(title=title)
        )
        return self._parse_outline(chat_hist)

    def _parse_outline(self, chat_hist):
        """
        Parse the mind map and outline text into a structured format.
        """
        # Prepare the response
        editor_messages = [mes for mes in chat_hist.chat_history if 'MINDMAP:' in mes['content'] and 'OUTLINE:' in mes['content']]

        if not editor_messages:
            return "NO mind map or outline from the Editor-in-Chief.", [], [], 0

        content = editor_messages[-1]['content']

        # Extract mind map
        mind_map = re.search(r'MINDMAP:(.*?)END_MINDMAP', content, re.DOTALL)
        mind_map = mind_map.group(1).strip() if mind_map else "NO mind map found."

        # Extract outline
        outline = re.search(r'OUTLINE:(.*?)END_OUTLINE', content, re.DOTALL)
        outline = outline.group(1).strip() if outline else "NO outline found."

        # Parse sections
        sections = re.findall(r'(\d+)\.\s+TITLE:\s+(.*?)\s+BRIEF:\s+(.*?)(?=\d+\.\s+TITLE:|$)', outline, re.DOTALL)

        titles = []
        briefs = []
        overall_word_count = 0

        for section in sections:
            titles.append(section[1].strip())
            brief = section[2].strip()
            briefs.append(brief)

            # Extract word count from brief
            word_count_match = re.search(r'WORD COUNT:\s*(\d+)', brief)
            if word_count_match:
                overall_word_count += int(word_count_match.group(1))

        # Write mind map, titles, briefs, and overall word count to markdown file
        result_dir = f'{self.project_config.project_dir}/results/{self.project_config.logging_session_id}'
        os.makedirs(result_dir, exist_ok=True)
        with open(f'{result_dir}/results-{self.project_config.logging_session_id}.md', 'w') as f:
            f.write("# Mind Map\n\n")
            f.write("```graphviz\n")
            f.write(mind_map)
            f.write("\n```\n\n")
            f.write(f"# Outline (Total Word Count: {overall_word_count})\n\n")
            for title, brief in zip(titles, briefs):
                f.write(f"## {title}\n\n")
                f.write(f"Brief: {brief}\n\n")

        # write the mind map in a dat file
        os.makedirs(f'{result_dir}/graphviz', exist_ok=True)
        with open(f'{result_dir}/graphviz/mind_map-{self.project_config.logging_session_id}.dat', 'w') as f:
            f.write(mind_map)

        return mind_map, titles, briefs, overall_word_count
