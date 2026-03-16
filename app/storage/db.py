import sqlite3
from pathlib import Path

DB_PATH = Path(r"E:\Work\.devmem\devmem.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True, parents=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        root_path TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        command TEXT NOT NULL,
        cwd TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT NOT NULL,
        duration_ms INTEGER NOT NULL,
        exit_code INTEGER NOT NULL,
        stdout TEXT,
        stderr TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        file_path TEXT,
        line_number INTEGER,
        error_type TEXT,
        message TEXT,
        traceback TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        followup_error_id INTEGER,
        resolved_by_run_id INTEGER,
        FOREIGN KEY (run_id) REFERENCES runs(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (followup_error_id) REFERENCES errors(id),
        FOREIGN KEY (resolved_by_run_id) REFERENCES runs(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs(id),
        FOREIGN KEY (project_id) REFERENCES projects(id)
    );""")
    conn.commit()
    conn.close()
