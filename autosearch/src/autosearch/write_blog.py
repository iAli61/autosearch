# In write_blog.py

from autosearch.research_project import ResearchProject
from autosearch.chat.outline_creator import OutlineCreator
from autosearch.chat.instruction_creator import InstructionCreator
from autosearch.chat.write_section import SectionWriter
from autosearch.agents.agents_creator import AgentsCreator
from typing_extensions import Annotated
import autogen
import importlib
import re


class WriteBlog(ResearchProject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instruction_creator = None
        self.outline_creator = None

    def run(self, title: str, target_audience: str):
        """
        Execute the entire research workflow.

        Args:
            title (str): The title of the article.
            target_audience (str): The target audience for the article.

        Returns:
            str: The final blog post.
        """
        self.title = title
        self.target_audience = target_audience

        # Create instruction
        self.instruction_creator = InstructionCreator(self.ProjectConfig, self.agents_groups['instructor_agents'])
        self.instruction = self.instruction_creator.run(title, target_audience, silent=False)
        # Create outline
        self.outline_creator = OutlineCreator(self.ProjectConfig, self.agents_groups['outline_agents'], max_round=150)

        def write_section(
                title: Annotated[str, "The title of the section."],
                brief: Annotated[str, "A clear, detailed brief about what the section should include."],
                mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
                silent: Annotated[bool, "It should always be True."] = True
        ):
            module = importlib.import_module('autosearch.communities.write_section_agents')
            agentsconfig = getattr(module, "agentsconfig")
            agents = AgentsCreator(self.ProjectConfig, agents_config=agentsconfig).initialize_agents()
            section_writer = SectionWriter(self.ProjectConfig, agents, max_round=20)
            return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)

        # find blog_editor agent in self.agents_groups['outline_agents']
        agents_dict = {k: v for d in self.agents_groups['outline_agents'] for k, v in d.items()}
        blog_editor = agents_dict.get("blog_editor-in-chief", None)
        if blog_editor is None:
            raise ValueError("No blog_editor-in-chief agent found in outline_agents")
        autogen.agentchat.register_function(
            f=write_section,
            name="write_section",
            caller=blog_editor,
            executor=agents_dict['editor_user'],
            description="Write a section based on the given title, brief, and mind map.",
        )

        mind_map, titles, briefs, overall_word_count = self.outline_creator.run(
            title=self.title,
            instruction=self.instruction,
            silent=False,
        )

        print(f"Overall word count: {overall_word_count}")

    def _write_sections(self, titles, briefs, mind_map):
        def write_section(
                title: Annotated[str, "The title of the section."],
                brief: Annotated[str, "A clear, detailed brief about what the section should include."],
                mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
                silent: Annotated[bool, "It should always be True."] = True
        ):
            module = importlib.import_module('autosearch.communities.write_section_agents')
            agentsconfig = getattr(module, "agentsconfig")
            agents = AgentsCreator(self.ProjectConfig, agents_config=agentsconfig).initialize_agents()
            section_writer = SectionWriter(self.ProjectConfig, agents, max_round=20)
            return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)

        agents_dict = {k: v for d in self.agents_groups['outline_agents'] for k, v in d.items()}
        blog_editor = agents_dict.get("blog_editor-in-chief", None)
        if blog_editor is None:
            raise ValueError("No blog_editor-in-chief agent found in outline_agents")

        autogen.agentchat.register_function(
            f=write_section,
            name="write_section",
            caller=blog_editor,
            executor=agents_dict['editor_user'],
            description="Write a section based on the given title, brief, and mind map.",
        )

        sections = []
        for title, brief in zip(titles, briefs):
            section = write_section(title=title, brief=brief, mind_map=mind_map)
            sections.append(section)

        return sections

    def postprocessing(self, sections):
        """
        Perform post-processing on the sections.

        Args:
            sections (List[str]): List of sections.

        Returns:
            Tuple[List[str], List[str]]: Tuple containing the processed section text and section references.
        """
        section_text = []
        section_refs = []
        for secs in sections:
            # split section based on "References" or "Citations" and "graphviz"
            if len(secs.split("References:")) > 1:
                section_text.append(secs.split("References:")[0].strip())
                remaining_text = secs.split("References:")[1]
                if len(remaining_text.split("```graphviz")) > 1:
                    section_refs.append(remaining_text.split("```graphviz")[0].strip())
                    section_text.append(remaining_text.split("```graphviz")[1].strip())
                else:
                    print(f"the following sections does not have graphviz: {secs}")
                    section_refs.append(remaining_text.strip())
            elif len(secs.split("Citations:")) > 1:
                section_text.append(secs.split("Citations:")[0].strip())
                remaining_text = secs.split("Citations:")[1]
                if len(remaining_text.split("```graphviz")) > 1:
                    section_refs.append(remaining_text.split("```graphviz")[0].strip())
                    section_text.append(remaining_text.split("```graphviz")[1].strip())
                else:
                    print(f"the following sections does not have graphviz: {secs}")
                    section_refs.append(remaining_text.strip())
            else:
                print(f"the following sections does not have Citations: {secs}")

        blog_sections = f"# {self.title}\n\n"
        blog_sections += "\n\n".join(f'## {i}. {section}' for i, section in enumerate(section_text, start=1))
        blog_sections += "Citations: \n"
        blog_sections += '\n'.join(section_refs)

        # remove "TXT", "TERMINATE", "END_TXT" from the blog_sections
        blog_sections = f"""{re.sub(r'TXT:|TERMINATE|END_TXT:|TXT|END_TXT', '', blog_sections)}"""

        blog_sections = blog_sections.strip()
        # print(blog_sections)

        with open(f'{self.result_dir}/blog_post-{self.logging_session_id}.md', 'w') as f:
            f.write(blog_sections)

        # read blog_sections
        with open(f'{self.result_dir}/blog_post-{self.logging_session_id}.md', 'r') as f:
            blog_sections = f.read()

        return blog_sections
