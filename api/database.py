"""
Database connection helper for the PGxBD API.

Provides a dependency-injectable SQLite connection with row factory.
"""

import sqlite3
from pathlib import Path

# Resolve database path relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _PROJECT_ROOT / "db" / "pgxbd.db"


def get_db():
    """
    FastAPI dependency that yields a SQLite connection with Row factory.
    The connection is closed automatically when the generator completes.
    """
    # check_same_thread=False: FastAPI dispatches a sync dependency's
    # pre-yield code and the endpoint body as separate anyio threadpool
    # calls, which are not guaranteed to land on the same OS thread. Each
    # request still gets its own private connection, so this is safe.
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_db_sync():
    """
    Synchronous connection helper for use outside of FastAPI dependency
    injection (e.g. in scripts or tests).
    """
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
