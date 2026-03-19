from dataclasses import dataclass, asdict, fields as dc_fields
import json
from pathlib import Path

DATA_FILE = Path("recipes.json")
FAVORITES_FILE = Path("favorites.json")
CATEGORIES_FILE = Path("categories.json")

DEFAULT_CATEGORIES: list[str] = ["Завтрак", "Обед", "Ужин", "Десерт"]
DIFFICULTIES: list[str] = ["🟢 Лёгкий", "🟡 Средний", "🔴 Сложный"]
COOK_TIMES: list[str] = ["15 мин", "30 мин", "45 мин", "1 час", "1.5 часа", "2+ часа"]


@dataclass
class Recipe:
    """Модель рецепта."""

    title: str
    ingredients: str
    steps: str
    image: str | None
    category: str
    cook_time: str | None = None
    difficulty: str | None = None


def load_categories() -> list[str]:
    """Загружает категории из файла; при отсутствии возвращает список по умолчанию."""
    if not CATEGORIES_FILE.exists():
        return list(DEFAULT_CATEGORIES)
    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(cats: list[str]) -> None:
    """Сохраняет список категорий в файл."""
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cats, f, ensure_ascii=False, indent=2)


def load_recipes() -> list[Recipe]:
    """Загружает рецепты из файла; при отсутствии возвращает пустой список."""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    valid_keys = {f.name for f in dc_fields(Recipe)}
    return [Recipe(**{k: v for k, v in item.items() if k in valid_keys}) for item in raw]


def save_recipes(recipes: list[Recipe]) -> None:
    """Сохраняет список рецептов в файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in recipes], f, ensure_ascii=False, indent=2)


def load_favorites() -> dict[int, list[str]]:
    """Загружает избранное из файла; при отсутствии возвращает пустой словарь."""
    if not FAVORITES_FILE.exists():
        return {}
    with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def save_favorites(data: dict[int, list[str]]) -> None:
    """Сохраняет данные избранного в файл."""
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in data.items()}, f, ensure_ascii=False, indent=2)


recipes: list[Recipe] = load_recipes()
categories: list[str] = load_categories()
user_browse_state: dict[int, dict] = {}
user_favorites: dict[int, list[str]] = load_favorites()


def search_recipes(query: str) -> list[Recipe]:
    """Возвращает рецепты, в названии или ингредиентах которых есть подстрока query."""
    q = query.strip().lower()
    if not q:
        return []
    return [
        r for r in recipes
        if q in r.title.lower() or q in r.ingredients.lower()
    ]


def delete_recipe(title: str) -> bool:
    """Удаляет рецепт по названию. Возвращает True если рецепт найден и удалён."""
    for i, r in enumerate(recipes):
        if r.title == title:
            recipes.pop(i)
            save_recipes(recipes)
            return True
    return False


def toggle_favorite(user_id: int, title: str) -> bool:
    """Добавляет/убирает из избранного. Возвращает True если добавлено."""
    favs = user_favorites.setdefault(user_id, [])
    if title in favs:
        favs.remove(title)
        save_favorites(user_favorites)
        return False
    favs.append(title)
    save_favorites(user_favorites)
    return True


def is_favorite(user_id: int, title: str) -> bool:
    """Проверяет, находится ли рецепт в избранном пользователя."""
    return title in user_favorites.get(user_id, [])


def get_favorites(user_id: int) -> list[Recipe]:
    """Возвращает список избранных рецептов пользователя."""
    titles = set(user_favorites.get(user_id, []))
    return [r for r in recipes if r.title in titles]


def get_filtered(category: str, user_id: int = 0) -> list[Recipe]:
    """Возвращает рецепты по категории; '__favorites__' — избранное пользователя."""
    if category == "__favorites__":
        return get_favorites(user_id)
    return [r for r in recipes if r.category == category]


def add_category(name: str) -> bool:
    """Добавляет новую категорию. Возвращает True если добавлена, False если уже есть."""
    norm = name.strip()
    if not norm:
        return False
    if norm.lower() in {c.lower() for c in categories}:
        return False
    categories.append(norm)
    save_categories(categories)
    return True


def delete_category(name: str) -> tuple[bool, str]:
    """Удаляет категорию. Возвращает (успех, причина_ошибки).
    Нельзя удалить встроенные или те, в которых есть рецепты."""
    if name in DEFAULT_CATEGORIES:
        return False, "default"
    if any(r.category == name for r in recipes):
        count = sum(1 for r in recipes if r.category == name)
        return False, f"has_recipes:{count}"
    if name not in categories:
        return False, "not_found"
    categories.remove(name)
    save_categories(categories)
    return True, ""