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
    
    
TRACEBACK_HEADER = "Traceback (most recent call last):"

def parse_regular_traceback(stderr:str) ->Optional[ParsedPythonTraceback]:
    if TRACEBACK_HEADER not in stderr:
        return None
    
    file_mathes = re.findall(r'File "(.+?)", line (\d+)', stderr)
    
    if not file_mathes:
        return None
    
    last_file_path, lat_line_number = file_mathes[-1]

    error_match = re.search(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.+)$", stderr.strip().splitlines()[-1])
    if not error_match:
        return None
    
    error_type = error_match.group(1)
    message = error_match.group(2)
    
    return ParsedPythonTraceback(
        traceback=stderr,
        file_path=last_file_path,
        line_number=int(lat_line_number),
        error_type=error_type,
        message=message,
    )
    

def parse_syntax_error(stderr:str)-> Optional[ParsedPythonTraceback]:
    lines = stderr.strip().splitlines()
    if not lines:
        return None
    
    last_line = lines[-1].strip()

    syntax_error_match = re.match(
        r"^([A-Za-z_][A-Za-z0-9_]*Error):\s*(.+)$",
        last_line,
    )
    if not syntax_error_match:
        return None
    
    error_type = syntax_error_match.group(1)
    message = syntax_error_match.group(2)
    
    if error_type not in {"SyntaxError","IndentationError", "TabError"}:
        return None
    
    file_match = re.search(r"File \"(.+?)\", line (\d+)", stderr)
    if not file_match:
        return ParsedPythonTraceback(
            file_path=None,
            line_number=None,
            error_type=error_type,
            message=message,
            traceback=stderr,
        )
        
    file_path = file_match.group(1)
    line_number = int(file_match.group(2))
    
    return ParsedPythonTraceback(
        file_path=file_path,
        line_number=line_number,
        error_type=error_type,
        message=message,
        traceback=stderr,
    )

def parse_python_traceback(stderr:str):
    parsed = parse_regular_traceback(stderr)
    if parsed is not None:
        return parsed
    
    parsed = parse_syntax_error(stderr)
    if parsed is not None:
        return parsed
    
    return None