import sys 
from app.runner.command_runner import run_command
from app.storage.db import init_db
def main() ->None:
    init_db()
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python main.py run <command> [args...]")
        return
    
    command_name = args[0]
    
    if command_name == "run":
        if len(args) < 2:
            print("Usage:")
            print("  python main.py run <command> [args...]")
            return
        
        command = args[1:]
        run_command(command)
        return
    
    print("Unknown command:", command_name)
    print("Usage:")
    print("  python main.py run <command> [args...]")