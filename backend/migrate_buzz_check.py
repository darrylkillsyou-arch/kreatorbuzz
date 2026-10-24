"""migrate_buzz_check.py — Phase 5 backward-safe DB migration.

Adds nullable metadata columns to shared_files and creates
the delivery_check_results table.  Safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "maccall.db"


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


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

    # ── shared_files: add Buzz Check metadata columns ──────────────────────────
    new_cols = [
        ("width", "INTEGER"),
        ("height", "INTEGER"),
        ("duration_seconds", "REAL"),
        ("deliverable_type", "TEXT"),
    ]
    for col_name, col_type in new_cols:
        if not column_exists(cur, "shared_files", col_name):
            cur.execute(f"ALTER TABLE shared_files ADD COLUMN {col_name} {col_type}")
            print(f"[ADD] shared_files.{col_name} ({col_type})")
        else:
            print(f"[SKIP] shared_files.{col_name} already exists")

    # ── delivery_check_results table ────────────────────────────────────────────
    if not table_exists(cur, "delivery_check_results"):
        cur.execute(
            """
            CREATE TABLE delivery_check_results (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id          INTEGER NOT NULL UNIQUE
                                 REFERENCES shared_files(id) ON DELETE CASCADE,
                workspace_id     INTEGER NOT NULL,
                version          INTEGER NOT NULL,
                overall_status   TEXT    NOT NULL,
                readiness_score  INTEGER NOT NULL,
                check_details    TEXT    NOT NULL DEFAULT '[]',
                warnings         TEXT    NOT NULL DEFAULT '[]',
                suggested_fixes  TEXT    NOT NULL DEFAULT '[]',
                generated_at     TEXT    NOT NULL
            )
            """
        )
        print("[CREATE] delivery_check_results table")
    else:
        print("[SKIP] delivery_check_results table already exists")

    conn.commit()
    conn.close()
    print("[DONE] Migration complete.")


if __name__ == "__main__":
    run()
