from dataclasses import dataclass
from typing import Optional

from app.storage.db import get_connection


@dataclass
class RunRecord:
    id: int
    project_id: int
    command: str
    cwd: str
    started_at: str
    finished_at: str
    duration_ms: int
    exit_code: int
    stdout: str
    stderr: str

def save_run(
    project_id: int,
    command: str,
    cwd: str,
    started_at: str,
    finished_at: str,
    duration_ms: int,
    exit_code: int,
    stdout: str,
    stderr: str,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO runs (
            project_id,
            command,
            cwd,
            started_at,
            finished_at,
            duration_ms,
            exit_code,
            stdout,
            stderr
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            command,
            cwd,
            started_at,
            finished_at,
            duration_ms,
            exit_code,
            stdout,
            stderr,
        ),
    )

    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id



def get_run_by_id(run_id: int) -> Optional[RunRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_id,
            command,
            cwd,
            started_at,
            finished_at,
            duration_ms,
            exit_code,
            stdout,
            stderr
        FROM runs
        WHERE id = ?
        """,
        (run_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return RunRecord(
        id=row[0],
        project_id=row[1],
        command=row[2],
        cwd=row[3],
        started_at=row[4],
        finished_at=row[5],
        duration_ms=row[6],
        exit_code=row[7],
        stdout=row[8],
        stderr=row[9],
    )
    
    
    
def get_next_run(project_id:int, run_id:int)->Optional[RunRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_id,
            command,
            cwd,
            started_at,
            finished_at,
            duration_ms,
            exit_code,
            stdout,
            stderr
        FROM runs
        WHERE project_id = ?
        AND id > ?
        ORDER BY id ASC
        LIMIT 1
        """,
        (project_id, run_id),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return RunRecord(
        id=row[0],
        project_id=row[1],
        command=row[2],
        cwd=row[3],
        started_at=row[4],
        finished_at=row[5],
        duration_ms=row[6],
        exit_code=row[7],
        stdout=row[8],
        stderr=row[9],
    )
    
    
def get_runs_for_project(project_id:int)->list[RunRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_id,
            command,
            cwd,
            started_at,
            finished_at,
            duration_ms,
            exit_code,
            stdout,
            stderr
        FROM runs
        WHERE project_id = ?
        ORDER BY id ASC
        """,
        (project_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        RunRecord(
            id=row[0],
            project_id=row[1],
            command=row[2],
            cwd=row[3],
            started_at=row[4],
            finished_at=row[5],
            duration_ms=row[6],
            exit_code=row[7],
            stdout=row[8],
            stderr=row[9],
        )
        for row in rows
    ]