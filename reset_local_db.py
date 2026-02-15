"""Reset local PostgreSQL database objects used by IZOTeacherBot.

This script drops the old pictures table and creates a new clean one.
It also optionally removes local shelve state files.

Usage (PowerShell examples):
  $env:DATABASE_URL="postgresql://postgres:password@localhost:5432/izoteacherbot"
  python reset_local_db.py
  python reset_local_db.py --keep-state
"""

import argparse
import os
from pathlib import Path

import psycopg2


CREATE_PIC_INFOS_SQL = """
CREATE TABLE IF NOT EXISTS pic_infos (
    id SERIAL PRIMARY KEY,
    file_id TEXT NOT NULL,
    author_name TEXT NOT NULL
);
"""

DROP_PIC_INFOS_SQL = "DROP TABLE IF EXISTS pic_infos;"


SHELVE_FILES = [
    Path("shelve.db.bak"),
    Path("shelve.db.dat"),
    Path("shelve.db.dir"),
]


def resolve_sslmode(database_url: str) -> str:
    ssl_mode = os.environ.get("DB_SSLMODE")
    if ssl_mode:
        return ssl_mode
    if "localhost" in database_url or "127.0.0.1" in database_url:
        return "disable"
    return "require"


def reset_database(database_url: str) -> None:
    ssl_mode = resolve_sslmode(database_url)
    try:
        connection = psycopg2.connect(database_url, sslmode=ssl_mode)
    except psycopg2.OperationalError as error:
        raise SystemExit(
            "Cannot connect to PostgreSQL.\n"
            "Check that PostgreSQL service is running and DATABASE_URL is correct.\n"
            "PowerShell quick check:\n"
            "  Test-NetConnection localhost -Port 5432\n"
            "If local Postgres uses no SSL, keep DB_SSLMODE unset (auto=disable for localhost)\n"
            f"Original error: {error}"
        )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DROP_PIC_INFOS_SQL)
                cursor.execute(CREATE_PIC_INFOS_SQL)
        print("Database reset completed: pic_infos dropped and recreated.")
    finally:
        connection.close()


def remove_local_state() -> None:
    removed = []
    for file_path in SHELVE_FILES:
        if file_path.exists():
            file_path.unlink()
            removed.append(str(file_path))

    if removed:
        print("Removed local shelve state files:", ", ".join(removed))
    else:
        print("No local shelve state files found.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Drop old pictures table and create a fresh local one."
    )
    parser.add_argument(
        "--keep-state",
        action="store_true",
        help="Do not remove local shelve state files.",
    )
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL is not set. Example: "
            "postgresql://postgres:password@localhost:5432/izoteacherbot"
        )

    reset_database(database_url)

    if not args.keep_state:
        remove_local_state()


if __name__ == "__main__":
    main()
