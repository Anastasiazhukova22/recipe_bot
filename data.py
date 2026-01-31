from dataclasses import dataclass, asdict
import json
from pathlib import Path

DATA_FILE = Path("recipes.json")


@dataclass
class Recipe:
    title: str
    ingredients: str
    steps: str
    image: str | None
    category: str


# ===== ЗАГРУЗКА / СОХРАНЕНИЕ =====

def load_recipes() -> list[Recipe]:
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return [Recipe(**item) for item in raw]


def save_recipes(recipes: list[Recipe]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [asdict(r) for r in recipes],
            f,
            ensure_ascii=False,
            indent=2
        )


# ===== ДАННЫЕ В ПАМЯТИ =====

recipes: list[Recipe] = load_recipes()

categories = ["Завтрак", "Обед", "Ужин", "Десерт"]

user_recipe_index: dict[int, int] = {}