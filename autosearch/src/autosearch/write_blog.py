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

Instruction = """
Dear Editor-in-Chief,
You are tasked with writing an article titled "Exploring the Intricacies of Polymer Representation: Unraveling Complexity" for a target audience of graduate students and early-career researchers in polymer science and materials engineering. This article should provide an in-depth exploration of polymer representation methods, their complexities, and their importance in advancing polymer science. Please follow these guidelines:

1-Introduction (300-400 words):
    - Begin with a brief overview of polymers and their significance in materials science.
    - Introduce the concept of polymer representation and why it's crucial for understanding and manipulating polymer properties.
    - Outline the main challenges in representing complex polymer structures.

2-Fundamental Concepts of Polymer Representation (500-600 words):
    - Explain the basic principles of polymer representation, including chemical structure, topology, and configuration.
    - Discuss the importance of accurately capturing both the molecular and macroscopic properties of polymers.
    - Introduce key terminology and concepts that will be used throughout the article.

3-Common Methods of Polymer Representation (600-700 words):
    - Describe and compare various methods used for representing polymers, such as:
        - Chemical formula representation
        - Graph-based representations
        - SMILES and SMARTS notations
        - Matrix-based representations
    - Explain the strengths and limitations of each method, providing examples where appropriate.

4-Advanced Techniques in Polymer Representation (700-800 words):
    - Explore cutting-edge approaches to polymer representation, such as:
        - Machine learning-based representations
        - Topological data analysis
        - Multiscale modeling approaches
    - Discuss how these advanced techniques address the limitations of traditional methods.
    - Provide examples of how these techniques have been applied in recent research.

5-Challenges and Complexities (500-600 words):
    - Delve into the difficulties of representing complex polymer systems, such as:
        - Branched and crosslinked polymers
        - Block copolymers and polymer blends
        - Dynamic and responsive polymers
    - Explain how these challenges impact polymer design, characterization, and application.

6- Applications and Future Directions (400-500 words):
    - Discuss the practical applications of polymer representation in various fields, such as drug delivery, materials engineering, and nanotechnology.
    - Explore emerging trends and future directions in polymer representation research.
    - Highlight the potential impact of improved representation methods on polymer science and technology.

7- Conclusion (200-300 words):
    - Summarize the key points discussed in the article.
    - Emphasize the importance of continued research in polymer representation for advancing materials science.
    - Encourage readers to explore the field further and consider its potential impact on their own research.

Throughout the article:

Use clear, concise language appropriate for graduate students and early-career researchers.
Incorporate relevant examples and case studies to illustrate complex concepts.
Include 2-3 figures or diagrams to visually represent key ideas (e.g., a comparison of different representation methods, a flowchart of the challenges in polymer representation).
Cite 10-15 recent, peer-reviewed sources to support your points and provide readers with resources for further reading.
Use analogies and real-world applications to make abstract concepts more relatable to the target audience.
Maintain a balance between technical depth and accessibility, ensuring that the content is challenging yet comprehensible for the intended readers.

Word count: Aim for a total of 3200-3900 words for the main body of the article (excluding references).
Remember to engage your audience by highlighting the exciting possibilities and challenges in this field, and how advancements in polymer representation can lead to breakthroughs in materials science and engineering.
"""


class WriteBlog(ResearchProject):
    def __init__(self, title, target_audience, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.target_audience = target_audience
        self.instruction = Instruction

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
        self.write_instruction()
        # Create outline
        self.outline_creator = OutlineCreator(self.ProjectConfig, self.agents_groups['outline_agents'], max_round=100)

        mind_map, titles, briefs, overall_word_count = self.outline_creator.run(
            title=self.title,
            instruction=self.instruction,
            silent=False,
        )

        print(f"Overall word count: {overall_word_count}")

        sections = self._write_sections(titles, briefs, mind_map)
        return self.postprocessing(sections)

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
