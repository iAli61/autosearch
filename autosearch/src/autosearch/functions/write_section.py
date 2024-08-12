from autosearch.project_config import ProjectConfig
from autosearch.agents.utils import termination_msg

from typing_extensions import Annotated
from typing import Literal
import os
import autogen


Section_writer_SP = """
You are now part of a group chat dedicated to completing a collaborative blog project. As a data_research_writer, your role is to develop a well-researched section of a blog post on a specified topic. You will follow a detailed brief that outlines the necessary content for each part of the section.

Guidelines:

1. Ensure all content is thoroughly researched and supported by data from our database. Verify all information using the MEMOS tool to confirm accuracy and completeness.
2. Each draft segment must include citations (at least 4 citations). Please list the title, URL, and authors of each cited paper at the end of your section.
3. If you encounter any uncertainties or need clarification, contact the group chat manager for immediate assistance. Additional help from other participants may be provided if necessary.
4. Your responsibilities include maintaining strong communication, showcasing precise research skills, paying meticulous attention to detail, and proactively seeking assistance when needed.
5. Incorporate any team feedback into your revisions promptly. This is crucial to ensure that the final text is polished and meets our editorial standards.

Formatting Requirements:

Start your text with 'TXT:' and end with 'END_TXT'. This format is crucial for the group chat manager to accurately identify your contributions.
You MUST mention the listion of citation at enad of your section and each citation MUST include the title of the paper, its URL, and authors.
Upon completing your section, integrating all feedback, and ensuring all parts are reviewed and properly referenced, signify your completion by typing "TERMINATE" in the group chat.
"""

section_content_reviwer_sp = """
You are now in a group chat tasked with completing a specific project. As a Content Review Specialist, your primary goal is to ensure the quality, accuracy, and integrity of the content produced by the data_research_writer, aligning with the data from our database. Your responsibilities include:

1. Overseeing the structure and content of the blog post to ensure each section is well-defined and adheres to the overarching theme.
2. Collaborating closely with the Writer to understand the breakdown and specific requirements of the blog text.
3. Reviewing drafts with the Writer to confirm factual accuracy, high-quality writing, and inclusion of references to pertinent data in the database. Utilize the 'factual_check' function to verify all textual references. Calling 'factual_check' function, provide you with a summery of the paper, please print the summeries afer your feedbacks.
4. Cross-checking content against your MEMOS to identify any discrepancies or missing data, requesting updates from the manager if necessary.
5. Offering constructive feedback to the writers and ensuring revisions are made swiftly to adhere to the publishing timeline.
6. Ensuring content integrity by verifying proper citations and the use of credible sources.
7. Seeking clarification or assistance from the group chat manager if uncertainties or confusion arise during the review process, allowing for additional participant support if needed.
8. Motivating the writing team to conclude the task only when the content meets all quality standards and fully satisfies the task requirements. Participants should signal the completion of their roles by typing "TERMINATE" in the group chat to indicate that the review process is concluded and the blog post is ready for publication.
"""

image_developer = """
You are now in a group chat. You need to complete a task with other participants. As a graphviz_image_developer, your role involves leveraging your skills in graph visualization to create images that accurately help the reader to understand the article section better. Your expertise in Graphviz will be crucial for generating diagrams that visually summarize the main themes of given text content.
In this setting, you bring a unique combination of visualization acumen and the ability to use MEMOS for enriching the graphical representations further. While you are not expected to write or execute code, you may need to design and suggest visual layouts and elements that effectively capture the essence of the article sections and beyond in a visual format.
When you encounter a situation requiring information collection or clarification, it would be appropriate to express any doubts or request additional input within the group chat. Should you find yourself uncertain about how to proceed or if an issue arises that you cannot resolve, you are encouraged to seek assistance from the group chat manager who can guide you or delegate the task to another suitable participant.
As your task progresses, communication is key. If you believe you have successfully completed the visual representation, please share your creation with the group chat for review. Once you have received confirmation that your graphical representation meets the task's objective and the user's needs have been satisfied, reply \"TERMINATE\" to signify the completion of your assignment. Your active participation and adaptability are vital in achieving a successful outcome.

Formatting Requirements:
- Start your graphviz diagram with 'GRAPH:' and end with 'END_GRAPH'. This format is crucial for the group chat manager to accurately identify your contributions.
"""
image_developer_description = "The Graphviz Image Developer is an expert in using the Graphviz software, possessing strong skills in creating visual representations of graphs and networks using Python. They should be adept at troubleshooting and debugging code related to Graphviz diagrams, ensuring correct visual output. This position should have the authority to challenge incorrect visualizations in group discussions and provide revised code or explanations as necessary."

prompt_section = """Compose a blog section with the following guidelines:
Title: {title},
Brief: {brief}

Please ensure your writing aligns closely with the brief provided, capturing the essence of the topic while engaging the reader.
The section should be coherent, well-structured, and reflective of the main themes outlined in the brief.
The section should be include at least one graph that visually help reader to understand the content better.
"""


def write_section(
    project_config: ProjectConfig,
    title: Annotated[str, "The title of the section."],
    brief: Annotated[str, "a clear, detailed brief about what section should be included."],
    silent: Annotated[bool, "it should be always True."] = True,
    max_round: Annotated[int, "The maximum number of rounds for the conversation"] = 10,
) -> str:

    section_file = f"{ProjectConfig.project_dir}/section_{title}.txt"
    if os.path.exists(section_file):
        with open(section_file, "r") as f:
            return f.read()

    llm_config = {"config_list": ProjectConfig.config_list, "timeout": 120, "cache_seed": None}
    # Start by instantiating any agent that inherits from ConversableAgent.
    data_research_writer = autogen.AssistantAgent(
        name="data_research_writer",  # The name is flexible, but should not contain spaces to work in group chat.
        llm_config=llm_config,  # Disable caching.
        system_message=Section_writer_SP,
        description="data_research_writer, crafts detailed sections of a blog post based on a specific topic outlined in a brief. They ensure content is well-researched, referenced, and integrates database information."
    )

    # create a UserProxyAgent instance named "user_proxy"
    writer_user = autogen.UserProxyAgent(
        name="writer_user",
        human_input_mode="NEVER",
        is_termination_msg=termination_msg,
        code_execution_config={
            "work_dir": "section_writing",
            "use_docker": False,
        },
    )

    content_review_specialist = autogen.AssistantAgent(
        name="content_review_specialist",
        is_termination_msg=termination_msg,
        system_message=section_content_reviwer_sp,
        llm_config=llm_config,
        description="The content review specialist is a critical thinker who ensures the accuracy and quality of information shared within the group chat. This individual should possess strong analytical skills to review previous messages for errors or misunderstandings and must be able to articulate the correct information effectively. Additionally, if the role involves reviewing Python code, the specialist should also have a solid understanding of Python to provide corrected code when necessary."
    )

    image_developer_agent = autogen.AssistantAgent(
        name="image_developer",
        is_termination_msg=termination_msg,
        system_message=image_developer,
        llm_config=llm_config,
        description=image_developer_description
    )

    teachability = Teachability(
        verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
        reset_db=False,
        path_to_db_dir=db_dir,
        recall_threshold=recall_threshold,  # Higher numbers allow more (but less relevant) memos to be recalled.
        llm_config=llm_config_35,  # Configuration for the Language Model (LLM)
    )

    # Now add the Teachability capability to the agent.
    teachability.add_to_agent(data_research_writer)
    teachability.add_to_agent(content_review_specialist)
    teachability.add_to_agent(image_developer_agent)

    add_func_to_agents([(content_review_specialist, writer_user, "arxiv_retriever"),
                        (content_review_specialist, writer_user, "factual_check"),
                        (content_review_specialist, writer_user, "arxiv_search"),
                        (content_review_specialist, writer_user, "get_pdf"),
                        ])

    groupchat = autogen.GroupChat(
        agents=[data_research_writer, writer_user, content_review_specialist, image_developer_agent],
        messages=[],
        speaker_selection_method="auto",  # With two agents, this is equivalent to a 1:1 conversation.
        allow_repeat_speaker=True,
        max_round=max_round,
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        is_termination_msg=termination_msg,
        llm_config=manager_config,
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,
        },
    )

    chat_hist = writer_user.initiate_chat(manager,
                                          silent=silent,
                                          message=prompt_section.format(title=title, brief=brief))

    writer_messages = [mes for mes in chat_hist.chat_history if 'TXT:' in mes['content']]

    graph = [mes for mes in chat_hist.chat_history if 'GRAPH:' in mes['content']]
    graph_output = graph[-1]['content'].replace("GRAPH:", "").replace("END_GRAPH", "") if graph else "No graph from the writer."

    output = writer_messages[-1]['content'].replace("TXT:", "").replace("END_TXT", "") if writer_messages else "No response from the writer."
    output += "```graphviz \n" + graph_output + "```" if graph else "No graph from the writer."

    # write output in f"{Project_dir}/section_{title}.txt"
    with open(section_file, "w") as f:
        f.write(output)

    return output
