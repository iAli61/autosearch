from autosearch.chat.group_chat import ResearchGroupChat
import autogen
import re
import os


def instruction_speaker_selection(last_speaker: autogen.Agent, groupchat: autogen.GroupChat):
    # Define the order of speakers
    speaker_order = [
        "topic_expert",
        "structure_specialist",
        "audience_adaptation_expert",
        "research_resource_expert",
        "instruction_synthesizer"
    ]

    # Get the index of the last speaker
    try:
        last_index = speaker_order.index(last_speaker.name)
    except ValueError:
        # If the last speaker is not in the list, start from the beginning
        return groupchat.agent_by_name(speaker_order[0])

    # Return the next speaker in the order
    next_index = (last_index + 1) % len(speaker_order)
    return groupchat.agent_by_name(speaker_order[next_index])


class InstructionCreator(ResearchGroupChat):
    """
    A specialized group chat for creating instructions for the Editor-in-Chief.
    """

    def __init__(self, project_config, agents, max_round=5):
        manager_config = {
            "system_message": """
            You are the manager overseeing the creation of instructions for the Editor-in-Chief.
            Your role is to ensure that all agents contribute their expertise and that the final
            instruction is comprehensive and clear. Monitor the conversation, provide guidance
            when necessary, and conclude the process when a satisfactory instruction has been created.
            """,
        }

        super().__init__(
            project_config=project_config,
            agents=agents,
            manager_config=manager_config,
            custom_speaker_selection_func=instruction_speaker_selection,
            max_round=max_round
        )

    def run(self, title: str, target_audience: str, silent: bool = False):
        """
        Execute the instruction creation process.

        Args:
            title (str): The title of the article for which instructions are being created.
            target_audience (str): The target audience for the article.
            silent (bool): Whether to run the chat silently or not.

        Returns:
            str: The final instruction for the Editor-in-Chief.
        """
        initial_message = f"""
        We need to create comprehensive instructions for the Editor-in-Chief to write an article titled:
        "{title}"

        The target audience for this article is: {target_audience}

        Each agent should contribute their expertise to craft a well-rounded instruction,
        keeping in mind the specific needs and background of the target audience.
        Topic Expert, please start by analyzing the title and providing key insights,
        considering how they should be presented to this audience.
        """

        chat_hist = self.agents_list[0].initiate_chat(
            self.manager,
            message=initial_message,
            silent=silent
        )

        return self._parse_final_instruction(chat_hist)

    def _parse_final_instruction(self, chat_hist):
        """
        Parse the chat history to extract the final instruction.

        Args:
            chat_hist: The chat history object.

        Returns:
            str: The final instruction for the Editor-in-Chief.
        """
        # Find the last message from the Instruction Synthesis Agent
        synthesizer_messages = [
            msg for msg in reversed(chat_hist.chat_history)
            if msg['role'] != 'assistant' and msg['name'] == 'instruction_synthesizer'
        ]

        if not synthesizer_messages:
            return "No final instruction found."

        final_message = synthesizer_messages[0]['content']

        # Extract the instruction from the final message
        instruction_match = re.search(r'FINAL INSTRUCTION:(.*?)(?:END INSTRUCTION|$)', final_message, re.DOTALL)

        if instruction_match:
            instruction = instruction_match.group(1).strip()
        else:
            instruction = "Failed to extract final instruction."

        # Save the instruction to a file
        result_dir = f'{self.project_config.project_dir}/results/{self.project_config.logging_session_id}'
        os.makedirs(result_dir, exist_ok=True)
        with open(f'{result_dir}/editor_instruction-{self.project_config.logging_session_id}.md', 'w') as f:
            f.write(f"# Editor-in-Chief Instruction\n\n{instruction}")

        return instruction
