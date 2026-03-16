from datetime import datetime
from pathlib import Path
import subprocess
from dataclasses import dataclass

from app.core.project_detector import detect_project
from app.storage.project_repository import get_or_create_project
from app.storage.run_repository import save_run
from app.parsers.python_traceback import parse_python_traceback
from app.core.error_fingerprint import build_error_fingerprint
from app.storage.error_repository import (
    get_active_errors_for_project,
    mark_error_resolved,
    mark_error_followup,
    create_error,
)
from app.storage.file_snapshot_repository import save_snapshot_for_run


@dataclass
class CommandRunResult:
    command: str
    cwd: str
    started_at: str
    finished_at: str
    duration_ms: int
    exit_code: int
    stdout: str
    stderr: str


def run_command(command: list[str]) -> None:
    cwd = Path.cwd()
    detected_project = detect_project(cwd)

    project = get_or_create_project(
        root_path=str(detected_project.root_path),
        name=detected_project.name,
    )

    started_at = datetime.now()

    print(f"[devmem] Project: {project.name}")
    print(f"[devmem] Project root: {project.root_path}")
    print(f"[devmem] Detection marker: {detected_project.detection_marker}")
    print(f"[devmem] Running: {' '.join(command)}")
    print(f"[devmem] Started at: {started_at.isoformat()}")
    print("-" * 60)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            shell=False,
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode

    except FileNotFoundError:
        stdout = ""
        stderr = f"Command not found: {command[0]}\n"
        exit_code = 127

    finished_at = datetime.now()
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)

    run_result = CommandRunResult(
        command=" ".join(command),
        cwd=str(cwd),
        started_at=started_at.isoformat(),
        finished_at=finished_at.isoformat(),
        duration_ms=duration_ms,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )

    if run_result.stdout:
        print(run_result.stdout, end="")

    if run_result.stderr:
        print(run_result.stderr, end="")

    print("-" * 60)
    print(f"[devmem] Exit code: {run_result.exit_code}")
    print(f"[devmem] Duration: {run_result.duration_ms} ms")
    print(f"[devmem] Finished at: {run_result.finished_at}")

    run_id = save_run(
        project_id=project.id,
        command=run_result.command,
        cwd=run_result.cwd,
        started_at=run_result.started_at,
        finished_at=run_result.finished_at,
        duration_ms=run_result.duration_ms,
        exit_code=run_result.exit_code,
        stdout=run_result.stdout,
        stderr=run_result.stderr,
    )

    print(f"[devmem] Saved run id: {run_id}")
    
    snapshot_count = save_snapshot_for_run(
        run_id=run_id,
        project_id=project.id,
        project_root=Path(project.root_path),
    )

    print(f"[devmem] Saved {snapshot_count} snapshots for run id: {run_id}")

    parsed_error = parse_python_traceback(run_result.stderr)

    if run_result.exit_code == 0:
        active_errors = get_active_errors_for_project(project.id)

        for error in active_errors:
            mark_error_resolved(error.id, run_id)
            print(f"[devmem] Resolved error id: {error.id}")

        return

    if parsed_error is None:
        print("[devmem] Run failed, but error was not parsed")
        return

    fingerprint = build_error_fingerprint(parsed_error, Path(project.root_path))
    active_errors = get_active_errors_for_project(project.id)

    existing_error = next(
        (error for error in active_errors if error.fingerprint == fingerprint),
        None,
    )

    if existing_error is not None:
        print(f"[devmem] Error already active: {existing_error.id}")
        return

    error_id = create_error(
        run_id=run_id,
        project_id=project.id,
        file_path=parsed_error.file_path,
        line_number=parsed_error.line_number,
        error_type=parsed_error.error_type,
        message=parsed_error.message,
        traceback=parsed_error.traceback,
        fingerprint=fingerprint,
    )
    print(f"[devmem] Saved error id: {error_id}")

    for error in active_errors:
        mark_error_followup(
            error_id=error.id,
            followup_error_id=error_id,
            resolved_by_run_id=run_id,
        )
        print(f"[devmem] Follow-up linked: {error.id} -> {error_id}")