from pathlib import Path
from dataclasses import dataclass

PROJECT_MARKERS = (
    ".git",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "manage.py",
    "package.json",
)



@dataclass
class DetectedProject:
    root_path: Path
    name: str
    detection_marker: str
    

def detect_project(start_path: Path) -> DetectedProject | None:
    current = start_path.resolve()
    
    for candidate in [current, *current.parents]:
        for marker in PROJECT_MARKERS:
            if (candidate / marker).exists():
                return DetectedProject(
                    name=candidate.name,
                    root_path=candidate,
                    detection_marker=marker,
                )
                
    return DetectedProject(
        root_path=current,
        name=current.name,
        detection_marker="cwd",
    )