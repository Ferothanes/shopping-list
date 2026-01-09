from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from . import supabase_store

def _cart_path() -> Path:
    return Path(__file__).resolve().parents[1] / "shopping_cart.json"


def load_cart() -> list[str]:
    if supabase_store.is_enabled():
        return supabase_store.list_items("shopping_cart_items")
    path = _cart_path()
    if not path.exists():
        save_cart([])
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    return sorted({item.strip().lower() for item in items if item.strip()})


def save_cart(items: Iterable[str]) -> None:
    if supabase_store.is_enabled():
        supabase_store.replace_items("shopping_cart_items", items)
        return
    path = _cart_path()
    cleaned = sorted({item.strip().lower() for item in items if item.strip()})
    payload = {"items": cleaned}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def add_to_cart(item: str) -> list[str]:
    if supabase_store.is_enabled():
        supabase_store.add_item("shopping_cart_items", item)
        return load_cart()
    items = load_cart()
    items.append(item)
    save_cart(items)
    return load_cart()


def remove_from_cart(item: str) -> list[str]:
    if supabase_store.is_enabled():
        supabase_store.remove_item("shopping_cart_items", item)
        return load_cart()
    items = [i for i in load_cart() if i != item.strip().lower()]
    save_cart(items)
    return items
