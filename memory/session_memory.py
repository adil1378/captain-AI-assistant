"""
Captain AI OS — Supabase PostgreSQL & SQLite-backed Session Memory Module.
Persists conversation turns (user + assistant) per session ID in Supabase PostgreSQL,
falling back to local SQLite if PostgreSQL is unreachable or unconfigured.
"""

import os
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Check for Supabase / Postgres connection string
_PG_URL = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")
if _PG_URL and _PG_URL.startswith("postgresql+asyncpg://"):
    _PG_URL = _PG_URL.replace("postgresql+asyncpg://", "postgresql://")

# Default SQLite database path for offline fallback
_SQLITE_DB_PATH = Path("./data/captain_memory.db")

_local = threading.local()
_pg_disabled: bool = False


def _get_pg_conn():
    """Attempt to establish or return thread-local psycopg2 PostgreSQL connection with fast fallback."""
    global _pg_disabled
    if _pg_disabled:
        return None

    import psycopg2
    from psycopg2.extras import RealDictCursor

    if not hasattr(_local, "pg_conn") or _local.pg_conn is None or _local.pg_conn.closed:
        if not _PG_URL:
            _pg_disabled = True
            return None
        try:
            conn = psycopg2.connect(_PG_URL, connect_timeout=2)
            conn.autocommit = True
            _init_pg_db(conn)
            _local.pg_conn = conn
            logger.info("SessionMemory: Connected to Supabase PostgreSQL.")
        except Exception as e:
            logger.warning(f"SessionMemory: Supabase PostgreSQL unreachable ({e}). Switching to fast local SQLite.")
            _pg_disabled = True
            return None
    return _local.pg_conn


def _init_pg_db(conn) -> None:
    """Create conversation_turns table in Supabase PostgreSQL if not exists."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id          SERIAL PRIMARY KEY,
                session_id  VARCHAR(255) NOT NULL,
                role        VARCHAR(50)  NOT NULL CHECK(role IN ('user', 'assistant')),
                content     TEXT         NOT NULL,
                created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_session_id ON conversation_turns(session_id, id);
        """)


def _get_sqlite_conn() -> sqlite3.Connection:
    """Return a thread-local SQLite connection as fallback."""
    if not hasattr(_local, "sqlite_conn") or _local.sqlite_conn is None:
        _SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(_SQLITE_DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _local.sqlite_conn = conn
        _init_sqlite_db(conn)
    return _local.sqlite_conn


def _init_sqlite_db(conn: sqlite3.Connection) -> None:
    """Create conversation_turns table in SQLite if not exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_turns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            role        TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
            content     TEXT    NOT NULL,
            created_at  DATETIME DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON conversation_turns(session_id, id)")
    conn.commit()


def save_turn(session_id: str, role: str, content: str) -> None:
    """Persist a single conversation turn to Supabase PostgreSQL (or SQLite fallback)."""
    pg_conn = _get_pg_conn()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO conversation_turns (session_id, role, content) VALUES (%s, %s, %s)",
                    (session_id, role, content)
                )
            logger.debug(f"SessionMemory [Supabase]: Saved '{role}' turn for '{session_id}'")
            return
        except Exception as e:
            logger.error(f"SessionMemory [Supabase Error]: {e}. Using SQLite fallback.")

    # Fallback to SQLite
    s_conn = _get_sqlite_conn()
    s_conn.execute(
        "INSERT INTO conversation_turns (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    s_conn.commit()
    logger.debug(f"SessionMemory [SQLite]: Saved '{role}' turn for '{session_id}'")


def get_history(session_id: str, limit: int = 20) -> List[Dict[str, str]]:
    """Retrieve the last `limit` turns for a given session, ordered oldest-first."""
    pg_conn = _get_pg_conn()
    if pg_conn:
        try:
            from psycopg2.extras import RealDictCursor
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT role, content FROM (
                        SELECT role, content, id
                        FROM conversation_turns
                        WHERE session_id = %s
                        ORDER BY id DESC
                        LIMIT %s
                    ) sub ORDER BY id ASC
                """, (session_id, limit))
                rows = cur.fetchall()
                return [{"role": r["role"], "content": r["content"]} for r in rows]
        except Exception as e:
            logger.error(f"SessionMemory [Supabase Get Error]: {e}. Falling back to SQLite.")

    # Fallback to SQLite
    s_conn = _get_sqlite_conn()
    cursor = s_conn.execute("""
        SELECT role, content FROM (
            SELECT role, content, id
            FROM conversation_turns
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        ) ORDER BY id ASC
    """, (session_id, limit))
    return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]


def clear_session(session_id: str) -> int:
    """Delete all stored turns for a given session."""
    deleted = 0
    pg_conn = _get_pg_conn()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                cur.execute("DELETE FROM conversation_turns WHERE session_id = %s", (session_id,))
                deleted = cur.rowcount
            logger.info(f"SessionMemory [Supabase]: Cleared {deleted} turns for session '{session_id}'")
            return deleted
        except Exception as e:
            logger.error(f"SessionMemory [Supabase Clear Error]: {e}")

    # Fallback to SQLite
    s_conn = _get_sqlite_conn()
    cursor = s_conn.execute("DELETE FROM conversation_turns WHERE session_id = ?", (session_id,))
    s_conn.commit()
    deleted = cursor.rowcount
    logger.info(f"SessionMemory [SQLite]: Cleared {deleted} turns for session '{session_id}'")
    return deleted


def list_sessions() -> List[str]:
    """Return all unique session IDs stored in the database."""
    pg_conn = _get_pg_conn()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                cur.execute("SELECT DISTINCT session_id FROM conversation_turns ORDER BY session_id")
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"SessionMemory [Supabase List Error]: {e}")

    s_conn = _get_sqlite_conn()
    cursor = s_conn.execute("SELECT DISTINCT session_id FROM conversation_turns ORDER BY session_id")
    return [row["session_id"] for row in cursor.fetchall()]
