from autosearch.functions.create_teachable_groupchat import create_teachable_groupchat


def memorization_skill(db_dir, config_list, verbosity=0):
    prompt = """
For each memorization task, initiate your process with 'MEMORIZE_ARTICLE:'  
Delve into the passage to discern and assess its key insights. If the content presents noteworthy information, make a point to memorize these details. 
Conversely, if the passage does not offer significant insights, there's no need to commit it to memory. 
Upon choosing to memorize, you MUST finalize your notes by including both the article's title and its URL, employing the format '[source: article_title, article_url]' for efficient future access and verification.
"""
    instract_assistant, instract_user = create_teachable_groupchat("instract_assistant", "instract_user", db_dir, config_list, verbosity=verbosity)

    instract_user.initiate_chat(instract_assistant, silent=True, message=prompt)
