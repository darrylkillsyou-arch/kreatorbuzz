"""migrate_rescue.py — Backward-safe SQLite migration for Project Rescue.

Creates the project_rescue_logs table if it does not already exist.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "maccall.db"


def table_exists(cursor, table: str) -> bool:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cursor.fetchone() is not None


def run():
    if not DB_PATH.exists():
        print(f"[SKIP] Database not found at {DB_PATH}. Nothing to migrate.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    if not table_exists(cur, "project_rescue_logs"):
        cur.execute(
            """
            CREATE TABLE project_rescue_logs (
                id                          INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id                INTEGER NOT NULL
                                            REFERENCES workspaces(id) ON DELETE CASCADE,
                action_type                 TEXT    NOT NULL,
                triggered_by_user_id        INTEGER NOT NULL
                                            REFERENCES users(id) ON DELETE CASCADE,
                health_score_at_trigger     INTEGER NOT NULL,
                health_status_at_trigger    TEXT    NOT NULL,
                notes                       TEXT,
                replacement_creator_user_id INTEGER
                                            REFERENCES users(id) ON DELETE SET NULL,
                created_at                  TEXT    NOT NULL
            )
            """
        )
        print("[CREATE] project_rescue_logs table")
    else:
        print("[SKIP] project_rescue_logs table already exists")

    conn.commit()
    conn.close()
    print("[DONE] Project Rescue migration complete.")


if __name__ == "__main__":
    run()
