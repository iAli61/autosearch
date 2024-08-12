from autosearch.database.paper_database import PaperDatabase
from autosearch.analysis.document_analyzer import DocumentAnalyzer
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ProjectConfig:
    """
    Dataclass to store project configuration.
    """
    paper_db: PaperDatabase
    doc_analyzer: DocumentAnalyzer
    project_dir: str
    db_dir: str
    config_list: List[Dict[str, Any]]
    initiate_db: bool
    functions: Optional[Any] = None
    logging_session_id: Optional[str] = None
