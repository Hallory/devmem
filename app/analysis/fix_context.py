from dataclasses import dataclass
from typing import Optional

from app.storage.error_repository import (
    ErrorRecord,
    get_error_by_id,
    get_error_by_run_id,
)
from app.storage.run_repository import RunRecord, get_run_by_id, get_next_run
from app.storage.file_snapshot_repository import get_changed_files_between_runs


@dataclass
class FixContext:
    error_id: int
    project_id: int
    from_run_id: int
    to_run_id: Optional[int]
    context_kind:str
    from_error_fingerprint: str
    target_run_exit_code: Optional[int]
    target_run_state: Optional[str]
    changed_files: dict[str, list[str]]


def determine_run_state(
    target_run: RunRecord,
    target_error: Optional[ErrorRecord],
) -> str:
    if target_run.exit_code == 0:
        return "success"
    if target_error is not None:
        return "failed_parsed"
    return "failed_unparsed"


def build_empty_fix_context(
    error: ErrorRecord,
    context_kind: str,
) -> FixContext:
    return FixContext(
        error_id=error.id,
        project_id=error.project_id,
        from_run_id=error.run_id,
        to_run_id=None,
        context_kind=context_kind,
        from_error_fingerprint=error.fingerprint,
        target_run_exit_code=None,
        target_run_state=None,
        changed_files={"added": [], "removed": [], "changed": []},
    )
    



def build_next_attempt_context(error_id:int)-> Optional[FixContext]:
    error = get_error_by_id(error_id)
    if error is None:
        return None

    current_run = get_run_by_id(error.run_id)
    if current_run is None:
        return None

    next_run = get_next_run(error.project_id, error.run_id)
    if next_run is None:
        return None
    
    next_error = get_error_by_run_id(next_run.id)
    changed_files = get_changed_files_between_runs(current_run.id, next_run.id)
    target_run_state = determine_run_state(next_run, next_error)
    
    return FixContext(
        error_id=error.id,
        project_id=error.project_id,
        from_run_id=current_run.id,
        to_run_id=next_run.id,
        context_kind="next_attempt",
        from_error_fingerprint=error.fingerprint,
        target_run_exit_code=next_run.exit_code,
        target_run_state=target_run_state,
        changed_files=changed_files
    )


def  build_resolution_context(error_id:int)->Optional[FixContext]:
    error = get_error_by_id(error_id)
    if error is None:
        return None
    
    current_run = get_run_by_id(error.id)
    if current_run is None:
        return None

    if error.resolved_by_run_id is None:
        return build_empty_fix_context(error, context_kind="resolution")

    target_run = get_run_by_id(error.resolved_by_run_id)
    if target_run is None:
        return None

    target_error = get_error_by_run_id(target_run.id)
    changed_files = get_changed_files_between_runs(current_run.id, target_run.id)
    target_run_state = determine_run_state(target_run, target_error)
    
    return FixContext(
        error_id=error.id,
        project_id=error.project_id,
        from_run_id=current_run.id,
        to_run_id=target_run.id,
        context_kind="resolution",
        from_error_fingerprint=error.fingerprint,
        target_run_exit_code=target_run.exit_code,
        target_run_state=target_run_state,
        changed_files=changed_files
    )
    
    
def build_fix_context(error_id:int)->Optional[FixContext]:
    return  build_resolution_context(error_id)