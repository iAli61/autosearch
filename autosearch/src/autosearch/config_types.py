# autosearch/config_types.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ProjectConfig:
    paper_db: Any
    doc_analyzer: Any
    project_dir: str
    db_dir: str
    config_list: List[Dict[str, Any]]
    initiate_db: bool
    functions: Optional[Any] = None
    logging_session_id: Optional[str] = None
