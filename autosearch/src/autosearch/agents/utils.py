# Termination message definition
termination_msg = (
    lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", "")).upper()
)
