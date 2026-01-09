from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Tuple

import requests
from dotenv import load_dotenv

from . import cache_db

load_dotenv()

BASE_URL = os.getenv("THEMEALDB_BASE_URL", "https://www.themealdb.com/api/json/v1/1")


def _freeze_params(params: dict[str, str] | None) -> Tuple[Tuple[str, str], ...]:
    if not params:
        return tuple()
    return tuple(sorted(params.items()))


@lru_cache(maxsize=256)
def _get_cached(path: str, params_items: Tuple[Tuple[str, str], ...]) -> dict[str, Any]:
    url = f"{BASE_URL}/{path}"
    response = requests.get(url, params=dict(params_items), timeout=15)
    response.raise_for_status()
    return response.json()


def _get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    return _get_cached(path, _freeze_params(params))


def filter_by_ingredient(ingredient: str) -> list[dict[str, str]]:
    cached = cache_db.get_cached_filter(ingredient)
    if cached is not None:
        return cached
    data = _get("filter.php", {"i": ingredient})
    meals = data.get("meals") or []
    cache_db.set_cached_filter(ingredient, meals)
    return meals


def lookup_meal(meal_id: str) -> dict[str, Any] | None:
    cached = cache_db.get_cached_meal(meal_id)
    if cached is not None:
        return cached
    data = _get("lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    if meals:
        cache_db.set_cached_meal(meal_id, meals[0])
        return meals[0]
    return None


def parse_ingredients(meal: dict[str, Any]) -> list[str]:
    ingredients: list[str] = []
    for i in range(1, 21):
        key = f"strIngredient{i}"
        value = (meal.get(key) or "").strip().lower()
        if value:
            ingredients.append(value)
    return ingredients
