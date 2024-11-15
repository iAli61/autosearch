# In write_blog.py

from autosearch.research_project import ResearchProject
from autosearch.chat.outline_creator import OutlineCreator
from autosearch.chat.instruction_creator import InstructionCreator
from autosearch.chat.write_section import SectionWriter
from autosearch.agents.agents_creator import AgentsCreator
from random import randint
from typing_extensions import Annotated
import importlib
import re
import os


class WriteBlog(ResearchProject):
    def __init__(self, title, target_audience, instruction=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.target_audience = target_audience
        if instruction is None:
            self.write_instruction()
        else:
            self.instruction = instruction

    def write_instruction(self):
        """
        Create the instruction for the blog post.

        Args:
            title (str): The title of the article.
            target_audience (str): The target audience for the article.
        """
        self.instruction_creator = InstructionCreator(self.ProjectConfig, self.agents_groups['instructor_agents'], max_round=20)
        self.instruction = self.instruction_creator.run(self.title, self.target_audience, silent=False)

    def run(self):
        """
        Execute the entire research workflow.

        Args:
            title (str): The title of the article.
            target_audience (str): The target audience for the article.

        Returns:
            str: The final blog post.
        """
        # Create outline
        self.outline_creator = OutlineCreator(self.ProjectConfig, self.agents_groups['outline_agents'], max_round=100)

        mind_map, titles, briefs, overall_word_count = self.outline_creator.run(
            title=self.title,
            instruction=self.instruction,
            silent=False,
        )

        print(f"Overall word count: {overall_word_count}")

        sections = self._write_sections(titles, briefs, mind_map)
        sections = self.postprocessing(sections)

        final_blog_post, final_post_file = self.compile_final_blog_post(self.ProjectConfig, self.title)
        print(f"Final blog post has been written to: {final_post_file}")
        return final_blog_post

    def _write_sections(self, titles, briefs, mind_map):
        def write_section(
                title: Annotated[str, "The title of the section."],
                brief: Annotated[str, "A clear, detailed brief about what the section should include."],
                mind_map: Annotated[str, "The Graphviz code for the mind map of the entire blog post."],
                silent: Annotated[bool, "It should always be True."] = True
        ):
            module = importlib.import_module('autosearch.communities.write_section_agents')
            agentsconfig = getattr(module, "agentsconfig")
            prefix = f"section_{randint(0, 1000)}"
            agents = AgentsCreator(self.ProjectConfig,
                                   agents_config=agentsconfig,
                                   prefix=prefix
                                   ).initialize_agents()
            section_writer = SectionWriter(self.ProjectConfig, agents, max_round=50)
            return section_writer.run(brief=brief, title=title, mind_map=mind_map, silent=silent)

        sections = []
        for title, brief in zip(titles, briefs):
            section_file = f'{self.result_dir}/section_{title}.md'
            if os.path.exists(section_file):
                with open(section_file, 'r') as f:
                    section = f.read()
            else:
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
        blog_sections += "\n\n".join(f'{section}' for section in section_text)
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

    @staticmethod
    def compile_final_blog_post(project_config, title):
        result_dir = f'{project_config.project_dir}/results/{project_config.logging_session_id}'

        # Read the outline file
        with open(f'{result_dir}/results-{project_config.logging_session_id}.md', 'r') as f:
            outline = f.read()

        # Extract the mind map
        mind_map_match = re.search(r'```graphviz\n(.*?)\n```', outline, re.DOTALL)
        mind_map = mind_map_match.group(1) if mind_map_match else ""

        # Extract titles from the outline
        titles = re.findall(r'## (.*?)\n', outline)

        # Compile the blog post
        blog_post = f"# {title}\n\n"
        blog_post += f"## Mind Map\n\n```graphviz\n{mind_map}\n```\n\n"

        all_references = []

        for title in titles:
            section_file = f"{result_dir}/section_{title}.md"
            if os.path.exists(section_file):
                with open(section_file, 'r') as f:
                    section_content = f.read()

                # Extract the main content (excluding BRIEF and MINDMAP)
                main_content = re.search(r'# .*?\n(.*?)\n## Coherence Feedback', section_content, re.DOTALL)
                if main_content:
                    blog_post += f"## {title}\n\n{main_content.group(1).strip()}\n\n"

                # Extract references
                references = re.search(r'Citations:(.*?)(?=```graphviz|$)', section_content, re.DOTALL)
                if references:
                    all_references.extend(references.group(1).strip().split('\n'))

                # Add the visualization
                visualization = re.search(r'```graphviz\n(.*?)\n```', section_content, re.DOTALL)
                if visualization:
                    blog_post += f"### Section Visualization\n\n```graphviz\n{visualization.group(1)}\n```\n\n"

        # Add all unique references at the end
        unique_references = list(set(all_references))
        blog_post += "\n## References\n\n"
        for ref in unique_references:
            blog_post += f"- {ref}\n"

        # Write the final blog post
        final_post_file = f'{result_dir}/final_blog_post-{project_config.logging_session_id}.md'
        with open(final_post_file, 'w') as f:
            f.write(blog_post)

        return blog_post, final_post_file
