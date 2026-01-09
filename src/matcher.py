from __future__ import annotations

from dataclasses import dataclass
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from . import api_themealdb


@dataclass
class RecipeMatch:
    id: str
    name: str
    thumbnail: str
    ingredients: list[str]
    missing: list[str]
    source: str
    details_url: str


SOURCE_MEALDB = "TheMealDB"


_MEASURE_WORDS = {
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "teaspoon",
    "teaspoons",
    "tsp",
    "oz",
    "ounce",
    "ounces",
    "g",
    "kg",
    "ml",
    "l",
    "lb",
    "lbs",
    "pound",
    "pinch",
    "dash",
    "slice",
    "slices",
    "clove",
    "cloves",
    "to",
    "taste",
}

_SINGULAR_OVERRIDES: dict[str, str] = {}

_IGNORE_SPICES = {
    "salt",
    "pepper",
    "black pepper",
    "white pepper",
    "paprika",
    "cumin",
    "coriander",
    "turmeric",
    "chili powder",
    "cinnamon",
    "water",
}

_EXCLUDE_CATEGORIES = {"dessert"}


def _singularize(token: str) -> str:
    if token in _SINGULAR_OVERRIDES:
        return _SINGULAR_OVERRIDES[token]
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 3 and not token.endswith(("ses", "xes", "zes")):
        return token[:-2]
    if token.endswith("s") and len(token) > 3 and not token.endswith(("ss", "us")):
        return token[:-1]
    return token


def _normalize_ingredient(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [token for token in cleaned.split() if token and not token.isdigit()]
    filtered = [_singularize(token) for token in tokens if token not in _MEASURE_WORDS]
    return " ".join(filtered).strip()


def _normalize_list(items: Iterable[str]) -> list[str]:
    normalized = {_normalize_ingredient(item) for item in items if item.strip()}
    return sorted({item for item in normalized if item})


def normalize_item(text: str) -> str:
    normalized = _normalize_list([text])
    return normalized[0] if normalized else ""


def _candidate_meal_ids(ingredients: Iterable[str], limit_per_ingredient: int = 20) -> set[str]:
    meal_ids: set[str] = set()
    for ingredient in ingredients:
        meals = api_themealdb.filter_by_ingredient(ingredient)
        for meal in meals[:limit_per_ingredient]:
            meal_id = meal.get("idMeal")
            if meal_id:
                meal_ids.add(meal_id)
    return meal_ids


def _match_themealdb(inventory: list[str], inventory_set: set[str], max_missing: int) -> list[RecipeMatch]:
    candidate_ids = sorted(_candidate_meal_ids(inventory))
    results: list[RecipeMatch] = []

    if not candidate_ids:
        return results

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {
            executor.submit(api_themealdb.lookup_meal, meal_id): meal_id
            for meal_id in candidate_ids
        }
        for future in as_completed(future_map):
            meal_id = future_map[future]
            try:
                meal = future.result()
            except Exception:
                continue
            if not meal:
                continue
            category = (meal.get("strCategory") or "").strip().lower()
            if category in _EXCLUDE_CATEGORIES:
                continue
            raw_ingredients = api_themealdb.parse_ingredients(meal)
            ingredients = _normalize_list(raw_ingredients)
            missing = [i for i in ingredients if i not in inventory_set and i not in _IGNORE_SPICES]
            if len(missing) <= max_missing:
                results.append(
                    RecipeMatch(
                        id=meal_id,
                        name=meal.get("strMeal", "Unknown"),
                        thumbnail=meal.get("strMealThumb", ""),
                        ingredients=ingredients,
                        missing=missing,
                        source=SOURCE_MEALDB,
                        details_url=f"https://www.themealdb.com/meal/{meal_id}",
                    )
                )
    return results


def match_recipes(
    inventory: Iterable[str], max_missing: int = 3, sources: Iterable[str] | None = None
) -> list[RecipeMatch]:
    normalized_inventory = _normalize_list(inventory)
    if not normalized_inventory:
        return []

    inventory_set = set(normalized_inventory)
    selected_sources = set(sources) if sources else {SOURCE_MEALDB}
    results: list[RecipeMatch] = []

    if SOURCE_MEALDB in selected_sources:
        results.extend(_match_themealdb(normalized_inventory, inventory_set, max_missing))

    results.sort(key=lambda r: (len(r.missing), r.name.lower(), r.source))
    return results


def match_recipes_by_ingredient(required: str, inventory: Iterable[str]) -> list[RecipeMatch]:
    normalized_required = normalize_item(required)
    if not normalized_required:
        return []

    normalized_inventory = _normalize_list(inventory)
    inventory_set = set(normalized_inventory)

    results: list[RecipeMatch] = []
    meals = api_themealdb.filter_by_ingredient(normalized_required)
    candidate_ids = [meal.get("idMeal") for meal in meals if meal.get("idMeal")]

    for meal_id in candidate_ids:
        meal = api_themealdb.lookup_meal(meal_id)
        if not meal:
            continue
        category = (meal.get("strCategory") or "").strip().lower()
        if category in _EXCLUDE_CATEGORIES:
            continue
        raw_ingredients = api_themealdb.parse_ingredients(meal)
        ingredients = _normalize_list(raw_ingredients)
        missing = [i for i in ingredients if i not in inventory_set and i not in _IGNORE_SPICES]
        results.append(
            RecipeMatch(
                id=meal_id,
                name=meal.get("strMeal", "Unknown"),
                thumbnail=meal.get("strMealThumb", ""),
                ingredients=ingredients,
                missing=missing,
                source=SOURCE_MEALDB,
                details_url=f"https://www.themealdb.com/meal/{meal_id}",
            )
        )

    results.sort(key=lambda r: (r.name.lower(), r.source))
    return results
