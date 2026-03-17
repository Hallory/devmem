from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from app.core.project_detector import detect_project
from app.storage.project_repository import get_project_by_root_path
from app.storage.run_repository import get_runs_for_project
from app.storage.error_repository import get_last_error_for_project
from app.analysis.fix_context import build_fix_context

from app.storage.run_repository import RunRecord
from app.storage.error_repository import ErrorRecord
from app.analysis.fix_context import FixContext


@dataclass
class ProjectContext:
    project_id: int
    last_run: Optional[RunRecord]
    last_error: Optional[ErrorRecord]
    fix_context: Optional[FixContext]
    
    

def build_project_context()->Optional[ProjectContext]:
    cwd = Path.cwd()
    detected_project = detect_project(cwd)
    
    project = get_project_by_root_path(str(detected_project.root_path))
    if not project:
        return None
    
    runs = get_runs_for_project(project.id)
    last_run = runs[0] if runs else None
    
    last_error = get_last_error_for_project(project.id)
    
    fix_context = None
    if last_error:
        fix_context = build_fix_context(last_error.id)
    
    return ProjectContext(project.id, last_run, last_error, fix_context)