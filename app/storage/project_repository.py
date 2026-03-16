from dataclasses import dataclass

from app.storage.db import get_connection



@dataclass
class ProjectRecord:
    id: int
    root_path: str
    name: str
    
    
def get_project_by_root_path(root_path:str)->ProjectRecord:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT id, root_path, name FROM projects
        WHERE root_path = ?
        """,
        (root_path,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return ProjectRecord(
        id=row[0],
        root_path=row[1],
        name=row[2],
    )
    
    
def create_project(root_path:str, name:str)->ProjectRecord:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO projects (root_path, name)
        VALUES (?, ?)
        """,
        (root_path, name)
    )
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return ProjectRecord(
        id=project_id,
        root_path=root_path,
        name=name,
    )
    
    
def get_or_create_project(root_path:str, name:str)->ProjectRecord:
    existing_project = get_project_by_root_path(root_path)
    
    if existing_project is not None:
        return existing_project
    
    return create_project(root_path, name)