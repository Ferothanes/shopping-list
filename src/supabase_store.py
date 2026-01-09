from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def is_enabled() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))


@lru_cache(maxsize=1)
def _client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "")
    return create_client(url, key)


def list_items(table: str) -> list[str]:
    response = _client().table(table).select("item").execute()
    data = response.data or []
    return sorted({row["item"].strip().lower() for row in data if row.get("item")})


def add_item(table: str, item: str) -> None:
    cleaned = item.strip().lower()
    if not cleaned:
        return
    _client().table(table).upsert({"item": cleaned}, on_conflict="item").execute()


def remove_item(table: str, item: str) -> None:
    cleaned = item.strip().lower()
    if not cleaned:
        return
    _client().table(table).delete().eq("item", cleaned).execute()


def replace_items(table: str, items: Iterable[str]) -> None:
    cleaned = sorted({item.strip().lower() for item in items if item.strip()})
    _client().table(table).delete().neq("item", "").execute()
    if cleaned:
        payload = [{"item": item} for item in cleaned]
        _client().table(table).upsert(payload, on_conflict="item").execute()
