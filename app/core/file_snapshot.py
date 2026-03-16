import hashlib
from pathlib import Path

def compute_file_hash(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()

def scan_python_files(root:Path)->list[Path]:
    return [
        path
        for path in root.rglob("**/*.py")
        if ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and ".git" not in path.parts
    ]