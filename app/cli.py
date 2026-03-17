import sys
from pathlib import Path

from app.analysis.fix_context import build_fix_context
from app.runner.command_runner import run_command
from app.storage.db import init_db
from app.core.project_detector import detect_project
from app.storage.error_repository import (
    get_last_error_for_project,
    get_errors_for_project,
    get_error_by_id,
)
from app.storage.project_repository import get_project_by_root_path, ProjectRecord
from app.storage.run_repository import get_runs_for_project, get_run_by_id

def print_usage() -> None:
    print("Usage:")
    print("  devmem run <command> [args...]")
    print("  devmem fix-context --error-id <id>")
    print("  devmem fix-context --last")
    print("  devmem errors")
    print("  devmem projects")
    print("  devmem show-run --id <id>")
    print("  devmem show-error --id <id>")


def print_file_group(title: str, files: list[str]) -> None:
    print(f"    {title}:")
    if not files:
        print("      - none")
        return

    for file_path in files:
        print(f"      - {file_path}")


def print_fix_context(error_id: int) -> None:
    context = build_fix_context(error_id)

    if context is None:
        print(f"Fix context not found for error id: {error_id}")
        return

    print("Fix Context")
    print(f"  error_id: {context.error_id}")
    print(f"  project_id: {context.project_id}")
    print(f"  from_run_id: {context.from_run_id}")
    print(f"  to_run_id: {context.to_run_id}")
    print(f"  from_error_fingerprint: {context.from_error_fingerprint}")
    print(f"  target_run_exit_code: {context.target_run_exit_code}")
    print(f"  target_run_state: {context.target_run_state}")
    print("  changed_files:")
    print_file_group("added", context.changed_files["added"])
    print_file_group("removed", context.changed_files["removed"])
    print_file_group("changed", context.changed_files["changed"])


def get_current_project()-> ProjectRecord | None:
    cwd = Path.cwd()
    detected_project = detect_project(cwd)
    return get_project_by_root_path(str(detected_project.root_path))


def print_last_fix_context() -> None:
    project = get_current_project()
    if project is None:
        print("Current project is not registered in devmem yet")
        return

    last_error = get_last_error_for_project(project.id)
    if last_error is None:
        print("No errors found for current project")
        return

    print_fix_context(last_error.id)


def print_errors() -> None:
    project = get_current_project()
    if project is None:
        print("Current project is not registered in devmem yet")
        return

    errors = get_errors_for_project(project.id)
    if not errors:
        print(f"No errors found for project: {project.name}")
        return

    print(f"Errors for project: {project.name}")
    print()

    for error in errors:
        print(
            f"- id={error.id:<4} | "
            f"run={error.run_id:<4} | "
            f"status={error.status:<28} | "
            f"{error.fingerprint}"
        )



def print_runs()->None:
    project = get_current_project()
    if project is None:
        print("Current project is not registered in devmem yet")
        return
    
    runs = get_runs_for_project(project.id)
    if not runs:
        print(f"No runs found for project: {project.name}")
        return

    print(f"Runs for project: {project.name}")
    print()

    for run in runs:
        print(
            f"- id={run.id:<4} | "
            f"exit={run.exit_code:<3} | "
            f"duration={run.duration_ms:<6}ms | "
            f"{run.command}"
        )
        
        
def print_run(run_id:int)->None:
    run = get_run_by_id(run_id)
    
    if run is None:
        print(f"Run not found: {run_id}")
        return
    
    print(f"Run: {run_id}")
    print()
    print(f"command: {run.command}")
    print(f"cwd: {run.cwd}")
    print(f"exit_code: {run.exit_code}")
    print(f"duration: {run.duration_ms}")
    print(f"started_at: {run.started_at}")
    print(f"finished_at: {run.finished_at}")
    print()

    print("stdout:")
    print(run.stdout or "<empty>")
    print()

    print("stderr:")
    print(run.stderr or "<empty>")
    


def print_error(error_id:int)->None:
    error = get_error_by_id(error_id)

    if error is None:
        print(f"Error not found: {error_id}")
        return

    print(f"Error: {error_id}")
    print()
    print(f"run_id: {error.run_id}")
    print(f"project_id: {error.project_id}")
    print(f"line_number: {error.line_number}")
    print(f"error_type: {error.error_type}")
    print(f"message: {error.message}")
    print(f"fingerprint: {error.fingerprint}")
    print(f"status: {error.status}")
    print(
        f"followup_error_id: "
        f"{error.followup_error_id if error.followup_error_id is not None else '<none>'}" 
    )
    print(
        f"resolved_by_run_id: "
        f"{error.resolved_by_run_id if error.resolved_by_run_id is not None else '<none>'}" 
    )
    print()
    print("traceback:")
    print(error.traceback or "<empty>")
    
    
def main() -> None:
    init_db()
    args = sys.argv[1:]

    if not args:
        print_usage()
        return

    command_name = args[0]

    if command_name == "run":
        if len(args) < 2:
            print_usage()
            return

        command = args[1:]
        run_command(command)
        return

    if command_name == "fix-context":
        if len(args) == 2 and args[1] == "--last":
            print_last_fix_context()
            return

        if len(args) == 3 and args[1] == "--error-id":
            try:
                error_id = int(args[2])
            except ValueError:
                print("error_id must be an integer")
                return

            print_fix_context(error_id)
            return

        print_usage()
        return

    if command_name == "errors":
        print_errors()
        return
    
    if command_name == "runs":
        print_runs()
        return
    
    if command_name == "show-run":
        if len(args) == 3 and args[1] == "--id":
            try:
                run_id = int(args[2])
            except ValueError:
                print("run_id must be an integer")
                return

            print_run(run_id)
            return
        
    
    if command_name == "show-error":
        if len(args) == 3 and args[1] == "--id":
            try:
                error_id = int(args[2])
            except ValueError:
                print("error_id must be an integer")
                return

            print_error(error_id)
            return

    print(f"Unknown command: {command_name}")
    print_usage()
