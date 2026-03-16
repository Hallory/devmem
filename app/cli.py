import sys 
from pathlib import Path

from app.analysis.fix_context import build_fix_context
from app.runner.command_runner import run_command
from app.storage.db import init_db
from app.core.project_detector import detect_project
from app.storage.error_repository import get_last_error_for_project
from app.storage.project_repository import get_project_by_root_path

def print_usage() -> None:
    print("Usage:")
    print("  devmem run <command> [args...]")
    print("  devmem fix-context --error-id <id>")
    print("  devmem fix-context --last")


def print_file_group(title:str, files:list[str])->None:
    print(f"    {title}:")
    if not files:
        print("     - none")
        return
    
    for file_path in files:
        print(f"     - {file_path}")

    
def print_fix_context(error_id:int)->None:
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
    print(f"  next_run_exit_code: {context.next_run_exit_code}")
    print(f"  next_run_state: {context.next_run_state}")
    print("  changed_files:")
    print_file_group("added ", context.changed_files['added'])
    print_file_group("removed ", context.changed_files['removed'])
    print_file_group("changed ", context.changed_files['changed'])
    
    
def print_last_fix_context()->None:
    cwd = Path.cwd()
    project_root = detect_project(cwd)
    
    project = get_project_by_root_path(str(project_root.root_path)) 
    if project is None:
        print("Current project is not registered in devmem yet")
        return
    
    last_error = get_last_error_for_project(project.id)
    if last_error is None:
        print("No errors found for current project")
        return
    
    print_fix_context(last_error.id)

def main() ->None:
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

    print(f"Unknown command: {command_name}")
    print_usage()