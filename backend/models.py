"""
models.py
SQLite persistence layer using Python's built-in sqlite3.
Stores game saves and analytics records.
"""

import sqlite3
import json
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "game.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS game_saves (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT UNIQUE NOT NULL,
            level       INTEGER NOT NULL,
            state_json  TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analytics_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            level           INTEGER NOT NULL,
            time_taken      REAL,
            moves           INTEGER,
            undo_count      INTEGER,
            failed_attempts INTEGER,
            won             INTEGER,
            heatmap_json    TEXT,
            recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ------------------------------------------------------------------ Saves

def save_game(session_id: str, level: int, state: dict):
    conn = get_connection()
    state_json = json.dumps(state)
    conn.execute("""
        INSERT INTO game_saves (session_id, level, state_json)
        VALUES (?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            level = excluded.level,
            state_json = excluded.state_json,
            updated_at = CURRENT_TIMESTAMP
    """, (session_id, level, state_json))
    conn.commit()
    conn.close()


def load_game(session_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM game_saves WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    if row:
        return {"session_id": row["session_id"], "level": row["level"],
                "state": json.loads(row["state_json"])}
    return None


# ------------------------------------------------------------------ Analytics

def record_analytics(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO analytics_records
            (session_id, level, time_taken, moves, undo_count, failed_attempts, won, heatmap_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("session_id"), data.get("level"), data.get("time_taken"),
        data.get("moves"), data.get("undo_count"), data.get("failed_attempts"),
        int(data.get("won", False)), json.dumps(data.get("heatmap", {}))
    ))
    conn.commit()
    conn.close()


def get_analytics_records() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM analytics_records ORDER BY recorded_at DESC LIMIT 200"
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "session_id": r["session_id"], "level": r["level"],
            "time_taken": r["time_taken"], "moves": r["moves"],
            "undo_count": r["undo_count"], "failed_attempts": r["failed_attempts"],
            "won": bool(r["won"]), "heatmap": json.loads(r["heatmap_json"] or "{}"),
            "recorded_at": r["recorded_at"],
        })
    return result