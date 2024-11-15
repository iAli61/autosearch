from autogen.code_utils import extract_code
from autogen.math_utils import get_answer

# Termination message definition
termination_msg = (
    lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", "")).upper()
)


def is_termination_msg_mathchat(message):
    """Check if a message is a termination message."""
    if isinstance(message, dict):
        message = message.get("content")
        if message is None:
            return False
    cb = extract_code(message)
    contain_code = False
    for c in cb:
        if c[0] == "python":
            contain_code = True
            break
    if message.rstrip().find("TERMINATE") >= 0:
        return True
    return not contain_code and get_answer(message) is not None and get_answer(message) != ""