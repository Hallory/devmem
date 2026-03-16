import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedPythonTraceback:
    traceback: str
    file_path: Optional[str]
    line_number: Optional[int]
    error_type: Optional[str]
    message: Optional[str]
    

def is_python_traceback(stderr:str):
    return "Traceback (most recent call last):" in stderr

def parse_python_traceback(stderr:str):
    """
    Parse a Python traceback from stderr.
    Returns ParsedPythonTraceback or None if not detected.
    """
    if not is_python_traceback(stderr):
        return None
    
    frames = re.findall(r"File \"(.+?)\", line (\d+), in (.+?)\n", stderr)
    
    if not frames:
        return None
    
    file_path = None
    line_number = None
    
    if frames:
        file_path, line_number, _ = frames[-1]
        line_number = int(line_number)
    
    
    error_match = re.search(r'(\w+(Error|Exception)):\s*(.+)', stderr)
    
    error_type = None
    message = None
    
    if error_match:
        error_type = error_match.group(1)
        message = error_match.group(3)

    return ParsedPythonTraceback(
        traceback=stderr,
        file_path=file_path,
        line_number=line_number,
        error_type=error_type,
        message=message,
    )