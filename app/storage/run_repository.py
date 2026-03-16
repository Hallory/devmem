from app.storage.db import get_connection


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
