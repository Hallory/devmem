from dataclasses import dataclass
from typing import Optional

from app.storage.db import get_connection


@dataclass
class ErrorRecord:
    id: int
    run_id: int
    project_id: int
    file_path: Optional[str]
    line_number: Optional[int]
    error_type: Optional[str]
    message: Optional[str]
    traceback: str
    fingerprint: str
    status: str
    followup_error_id: Optional[int]
    resolved_by_run_id: Optional[int]


def create_error(
    run_id: int,
    project_id: int,
    file_path: Optional[str],
    line_number: Optional[int],
    error_type: Optional[str],
    message: Optional[str],
    traceback: str,
    fingerprint: str,
    followup_error_id: Optional[int] = None,
    resolved_by_run_id: Optional[int] = None,
    status: str = "active",
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO errors (
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            followup_error_id,
            resolved_by_run_id,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            followup_error_id,
            resolved_by_run_id,
            status,
        ),
    )

    error_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return error_id


def get_errors_by_run(run_id: int) -> list[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE run_id = ?
        ORDER BY id ASC
        """,
        (run_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        ErrorRecord(
            id=row[0],
            run_id=row[1],
            project_id=row[2],
            file_path=row[3],
            line_number=row[4],
            error_type=row[5],
            message=row[6],
            traceback=row[7],
            fingerprint=row[8],
            status=row[9],
            followup_error_id=row[10],
            resolved_by_run_id=row[11],
        )
        for row in rows
    ]


def get_active_errors_for_project(project_id: int) -> list[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE project_id = ?
          AND status = 'active'
        ORDER BY id ASC
        """,
        (project_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        ErrorRecord(
            id=row[0],
            run_id=row[1],
            project_id=row[2],
            file_path=row[3],
            line_number=row[4],
            error_type=row[5],
            message=row[6],
            traceback=row[7],
            fingerprint=row[8],
            status=row[9],
            followup_error_id=row[10],
            resolved_by_run_id=row[11],
        )
        for row in rows
    ]
    
    
def mark_error_resolved(error_id:int, resolved_by_run_id:int)->None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE errors
        SET status = 'resolved',
            resolved_by_run_id = ?
        WHERE id = ?
        """,
        (resolved_by_run_id, error_id),
    )

    conn.commit()
    conn.close()
    
    
def mark_error_followup(
    error_id:int,
    followup_error_id:int,
    resolved_by_run_id:int,
)->None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE errors
        SET status = 'resolved_with_followup_error',
            followup_error_id = ?,
            resolved_by_run_id = ?
        WHERE id = ?
        """,
        (followup_error_id, resolved_by_run_id, error_id),
    )

    conn.commit()
    conn.close()
    
    
    
    
def get_error_by_id(error_id:int)->Optional[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE id = ?
        """,
        (error_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return ErrorRecord(
        id=row[0],
        run_id=row[1],
        project_id=row[2],
        file_path=row[3],
        line_number=row[4],
        error_type=row[5],
        message=row[6],
        traceback=row[7],
        fingerprint=row[8],
        status=row[9],
        followup_error_id=row[10],
        resolved_by_run_id=row[11],
    )
    
    
def get_error_by_run_id(run_id:int)->Optional[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE run_id = ?
        ORDER BY id ASC
        LIMIT 1
        """,
        (run_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return ErrorRecord(
        id=row[0],
        run_id=row[1],
        project_id=row[2],
        file_path=row[3],
        line_number=row[4],
        error_type=row[5],
        message=row[6],
        traceback=row[7],
        fingerprint=row[8],
        status=row[9],
        followup_error_id=row[10],
        resolved_by_run_id=row[11],
    )
    
    
    
    
def get_last_error_for_project(project_id:int)->Optional[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE project_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (project_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return ErrorRecord(
        id=row[0],
        run_id=row[1],
        project_id=row[2],
        file_path=row[3],
        line_number=row[4],
        error_type=row[5],
        message=row[6],
        traceback=row[7],
        fingerprint=row[8],
        status=row[9],
        followup_error_id=row[10],
        resolved_by_run_id=row[11],
    )
    
    
def get_errors_for_project(project_id:int)->list[ErrorRecord]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            project_id,
            file_path,
            line_number,
            error_type,
            message,
            traceback,
            fingerprint,
            status,
            followup_error_id,
            resolved_by_run_id
        FROM errors
        WHERE project_id = ?
        ORDER BY id ASC
        """,
        (project_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        ErrorRecord(
            id=row[0],
            run_id=row[1],
            project_id=row[2],
            file_path=row[3],
            line_number=row[4],
            error_type=row[5],
            message=row[6],
            traceback=row[7],
            fingerprint=row[8],
            status=row[9],
            followup_error_id=row[10],
            resolved_by_run_id=row[11],
        )
        for row in rows
    ]