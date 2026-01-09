from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

DEFAULT_INVENTORY = {"items": []}


def _inventory_path() -> Path:
    return Path(__file__).resolve().parents[1] / "inventory.json"


def load_inventory() -> list[str]:
    path = _inventory_path()
    if not path.exists():
        save_inventory([])
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    return sorted({item.strip().lower() for item in items if item.strip()})


def save_inventory(items: Iterable[str]) -> None:
    path = _inventory_path()
    cleaned = sorted({item.strip().lower() for item in items if item.strip()})
    payload = {"items": cleaned}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def add_item(item: str) -> list[str]:
    items = load_inventory()
    items.append(item)
    save_inventory(items)
    return load_inventory()


def remove_item(item: str) -> list[str]:
    items = [i for i in load_inventory() if i != item.strip().lower()]
    save_inventory(items)
    return items