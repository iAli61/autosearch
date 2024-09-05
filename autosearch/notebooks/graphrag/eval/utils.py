
import nest_asyncio
nest_asyncio.apply()

from typing import List, Dict
import re

def parse_evaluation_table(evaluation: str) -> Dict[str, Dict[str, float]]:
    try:
        table_text = evaluation.split("EVALUATION TABLE")[1].split("TERMINATE")[0].strip()
        lines = table_text.split("\n")
        scores = {}
        for line in lines:
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 3 and not is_header_or_separator_row(parts):
                criterion = parts[0].lower().replace(" ", "_")
                try:
                    local_score = parse_score(parts[-2])  # Second to last part
                    global_score = parse_score(parts[-1])  # Last part
                    scores[criterion] = {"local": local_score, "global": global_score}
                except ValueError as e:
                    print(f"Warning: {str(e)} for criterion {criterion}")
        
        if not scores:
            raise ValueError("No valid scores found in the evaluation table")
        
        return scores
    except Exception as e:
        print(f"Error parsing evaluation table: {str(e)}")
        return {}

def is_header_or_separator_row(parts: List[str]) -> bool:
    # Check if it's a header row
    if any(header.lower() in " ".join(parts).lower() for header in ["criterion", "local score", "global score"]):
        return True
    
    # Check if it's a separator row (contains only dashes, possibly with colons for alignment)
    if all(re.match(r'^[-:]+$', part) for part in parts):
        return True
    
    return False

def parse_score(score_str: str) -> float:
    score_str = score_str.strip().lower()
    if score_str in ['n/a', ''] or not re.search(r'\d', score_str):
        return math.nan  # Use NaN to represent N/A, empty scores, or non-numeric entries
    try:
        score = float(score_str)
        if 1 <= score <= 10:
            return score
        else:
            raise ValueError(f"Score out of range: {score}")
    except ValueError:
        raise ValueError(f"Invalid score format: {score_str}")
