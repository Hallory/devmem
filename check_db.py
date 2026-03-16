import sqlite3
from pathlib import Path
from app.storage.db import DB_PATH
from app.storage.file_snapshot_repository import get_changed_files_between_runs

print(get_changed_files_between_runs(14,15))
def print_table(cursor, table_name):
    print(f"\n===== {table_name.upper()} =====")

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print("table empty")
        return

    for row in rows:
        print(row)


def main():
    if not DB_PATH.exists():
        print("Database not found:", DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_table(cursor, "projects")
    print_table(cursor, "runs")
    print_table(cursor, "errors")
    print_table(cursor, "file_snapshots")
    conn.close()


if __name__ == "__main__":
    main()