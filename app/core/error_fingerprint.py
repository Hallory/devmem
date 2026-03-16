import re
from pathlib import Path

from app.parsers.python_traceback import ParsedPythonTraceback


def normalize_error_message(message: str | None) -> str:
    if not message:
        return ""

    normalized = message

    normalized = re.sub(r"'[^']*'", "<str>", normalized)
    normalized = re.sub(r'"[^"]*"', "<str>", normalized)
    normalized = re.sub(r"\b\d+\b", "<num>", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def build_error_fingerprint(
    parsed_error: ParsedPythonTraceback,
    project_root: Path,
) -> str:
    relative_path = ""

    if parsed_error.file_path:
        try:
            relative_path = str(Path(parsed_error.file_path).resolve().relative_to(project_root.resolve()))
        except ValueError:
            relative_path = Path(parsed_error.file_path).name

    normalized_message = normalize_error_message(parsed_error.message)
    error_type = parsed_error.error_type or ""

    return f"{relative_path}:{error_type}:{normalized_message}"