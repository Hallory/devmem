from pathlib import Path
from dataclasses import dataclass

from app.core.file_snapshot import compute_file_hash,scan_python_files
from app.storage.db import get_connection



@dataclass
class FileSnapshotRecord:
    id: int
    run_id: int
    project_id: int
    file_path: str
    content_hash: str

def create_file_snapshot(
    run_id:int,
    project_id:int,
    file_path:str,
    content_hash:str,
)->int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO file_snapshots (
            run_id,
            project_id,
            file_path,
            content_hash
        )
        VALUES (?, ?, ?, ?)
        """,
        (run_id, project_id, file_path, content_hash),
    )
    snapshot_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return snapshot_id

    
def save_snapshot_for_run(run_id:int, project_id:int,project_root:Path)->int:
    python_files = scan_python_files(project_root)
    saved_count = 0
    
    for path in python_files:
        content_hash = compute_file_hash(path)
        
        create_file_snapshot(
            run_id=run_id,
            project_id=project_id,
            file_path=str(path),
            content_hash=content_hash
        )
        saved_count += 1

    return saved_count


def get_snapshots_by_run(run_id:int) -> list[FileSnapshotRecord]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT id, run_id, project_id, file_path, content_hash
        FROM file_snapshots
        WHERE run_id = ?
        ORDER BY id ASC
        """,
        (run_id,)
        
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        FileSnapshotRecord(
            id=row[0],
            run_id=row[1],
            project_id=row[2],
            file_path=row[3],
            content_hash=row[4],
        )
        for row in rows
    ]
    
    

def get_changed_files_between_runs(from_run_id: int, to_run_id: int) -> dict[str, list[str]]:
    from_snapshots = get_snapshots_by_run(from_run_id)
    to_snapshots = get_snapshots_by_run(to_run_id)

    from_map = {snapshot.file_path: snapshot.content_hash for snapshot in from_snapshots}
    to_map = {snapshot.file_path: snapshot.content_hash for snapshot in to_snapshots}

    from_files = set(from_map.keys())
    to_files = set(to_map.keys())

    added = sorted(list(to_files - from_files))
    removed = sorted(list(from_files - to_files))
    changed = sorted([
        file_path
        for file_path in (from_files & to_files)
        if from_map[file_path] != to_map[file_path]
    ])

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
    }