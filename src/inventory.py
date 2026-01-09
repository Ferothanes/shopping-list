from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from . import supabase_store

DEFAULT_INVENTORY = {"items": []}


def _inventory_path() -> Path:
    return Path(__file__).resolve().parents[1] / "inventory.json"


def load_inventory() -> list[str]:
    if supabase_store.is_enabled():
        return supabase_store.list_items("inventory_items")
    path = _inventory_path()
    if not path.exists():
        save_inventory([])
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    return sorted({item.strip().lower() for item in items if item.strip()})


def save_inventory(items: Iterable[str]) -> None:
    if supabase_store.is_enabled():
        supabase_store.replace_items("inventory_items", items)
        return
    path = _inventory_path()
    cleaned = sorted({item.strip().lower() for item in items if item.strip()})
    payload = {"items": cleaned}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def add_item(item: str) -> list[str]:
    if supabase_store.is_enabled():
        supabase_store.add_item("inventory_items", item)
        return load_inventory()
    items = load_inventory()
    items.append(item)
    save_inventory(items)
    return load_inventory()


def remove_item(item: str) -> list[str]:
    if supabase_store.is_enabled():
        supabase_store.remove_item("inventory_items", item)
        return load_inventory()
    items = [i for i in load_inventory() if i != item.strip().lower()]
    save_inventory(items)
    return items
