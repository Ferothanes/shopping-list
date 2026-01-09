from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "recipes_cache.db"
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meals (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingredient_map (
                ingredient TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )


def get_cached_meal(meal_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload, updated_at FROM meals WHERE id = ?", (meal_id,)
        ).fetchone()
    if not row:
        return None
    payload, updated_at = row
    if int(time.time()) - int(updated_at) > CACHE_TTL_SECONDS:
        return None
    return json.loads(payload)


def set_cached_meal(meal_id: str, payload: dict[str, Any]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO meals (id, payload, updated_at) VALUES (?, ?, ?)",
            (meal_id, json.dumps(payload), int(time.time())),
        )


def get_cached_filter(ingredient: str) -> list[dict[str, Any]] | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload, updated_at FROM ingredient_map WHERE ingredient = ?",
            (ingredient,),
        ).fetchone()
    if not row:
        return None
    payload, updated_at = row
    if int(time.time()) - int(updated_at) > CACHE_TTL_SECONDS:
        return None
    return json.loads(payload)


def clear_cache() -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM meals")
        conn.execute("DELETE FROM ingredient_map")


def set_cached_filter(ingredient: str, payload: list[dict[str, Any]]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ingredient_map (ingredient, payload, updated_at) VALUES (?, ?, ?)",
            (ingredient, json.dumps(payload), int(time.time())),
        )
