"""Persistent deletion stats backed by SQLite."""

from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

# Store the DB in /data if available (Railway volume), else current dir.
_DB_DIR = Path(os.environ.get("DATA_DIR", "."))
_DB_PATH = _DB_DIR / "stats.db"


def _connect() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS deletions ("
        "  chat_id INTEGER NOT NULL,"
        "  day     TEXT    NOT NULL,"
        "  count   INTEGER NOT NULL DEFAULT 0,"
        "  PRIMARY KEY (chat_id, day)"
        ")"
    )
    conn.commit()
    return conn


def record_deletion(chat_id: int, n: int = 1) -> None:
    """Increment today\'s deletion counter for *chat_id*."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = _connect()
    conn.execute(
        "INSERT INTO deletions (chat_id, day, count) VALUES (?, ?, ?)"
        "  ON CONFLICT(chat_id, day) DO UPDATE SET count = count + ?",
        (chat_id, today, n, n),
    )
    conn.commit()
    conn.close()


def get_today_count(chat_id: int) -> int:
    """Return how many service messages were deleted today (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = _connect()
    row = conn.execute(
        "SELECT count FROM deletions WHERE chat_id = ? AND day = ?",
        (chat_id, today),
    ).fetchone()
    conn.close()
    return row[0] if row else 0


def get_count_for_date(chat_id: int, d: date) -> int:
    """Return deletions for a specific date."""
    conn = _connect()
    row = conn.execute(
        "SELECT count FROM deletions WHERE chat_id = ? AND day = ?",
        (chat_id, d.isoformat()),
    ).fetchone()
    conn.close()
    return row[0] if row else 0


def get_all_today_counts() -> dict[int, int]:
    """Return {chat_id: count} for every group with deletions today."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = _connect()
    rows = conn.execute(
        "SELECT chat_id, count FROM deletions WHERE day = ? AND count > 0",
        (today,),
    ).fetchall()
    conn.close()
    return {chat_id: count for chat_id, count in rows}
