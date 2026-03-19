import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from data import (
    recipes, categories, user_browse_state,
    is_favorite, delete_recipe,
    get_filtered,
)
from keyboards.main import (
    categories_kb, nav_kb, main_menu_kb,
    recipe_inline_kb, delete_confirm_kb, search_results_kb,
)
from handlers.common import send_recipe

router = Router()


def extract_category(text: str) -> str | None:
    """Извлекает название категории из текста кнопки вида 'Завтрак (3)'."""
    for cat in categories:
        if text == cat or text.startswith(f"{cat} ("):
            return cat
    return None


async def _navigate(message: Message, offset: int) -> None:
    """Листает рецепты текущей категории пользователя на offset позиций."""
    user_id = message.from_user.id
    state = user_browse_state.get(user_id)
    if not state:
        await message.answer("Сначала выберите категорию 📖", reply_markup=main_menu_kb())
        return
    category = state["category"]
    filtered = get_filtered(category, user_id)
    if not filtered:
        await message.answer("Рецептов нет 😔", reply_markup=main_menu_kb())
        return
    new_idx = (state["index"] + offset) % len(filtered)
    user_browse_state[user_id]["index"] = new_idx
    label = "⭐ Избранное" if category == "__favorites__" else f"<b>{category}</b>"
    await message.answer(
        f"{label} — рецепт {new_idx + 1} из {len(filtered)}:",
        reply_markup=nav_kb(),
    )
    await send_recipe(message, filtered[new_idx])


@router.message(F.text == "📖 Рецепты")
async def choose_category(message: Message) -> None:
    """Показывает список категорий для выбора."""
    await message.answer("Выберите категорию:", reply_markup=categories_kb())


@router.message(lambda m: bool(extract_category(m.text or "")))
async def show_category(message: Message) -> None:
    """Открывает первый рецепт выбранной категории."""
    category = extract_category(message.text)
    user_id = message.from_user.id
    filtered = get_filtered(category, user_id)

    if not filtered:
        await message.answer(
            f"В категории <b>{category}</b> пока нет рецептов 😔",
            reply_markup=main_menu_kb(),
        )
        return

    user_browse_state[user_id] = {"category": category, "index": 0}
    await message.answer(
        f"<b>{category}</b> — рецепт 1 из {len(filtered)}:",
        reply_markup=nav_kb(),
    )
    await send_recipe(message, filtered[0])


@router.message(F.text == "➡️ Вперёд")
async def next_recipe(message: Message) -> None:
    """Переходит к следующему рецепту в текущей категории."""
    await _navigate(message, 1)


@router.message(F.text == "⬅️ Назад")
async def prev_recipe(message: Message) -> None:
    """Переходит к предыдущему рецепту в текущей категории."""
    await _navigate(message, -1)


@router.message(F.text == "🎲 Случайный")
async def random_recipe(message: Message) -> None:
    """Показывает случайный рецепт и устанавливает позицию в его категории."""
    if not recipes:
        await message.answer("Рецептов пока нет 🥺", reply_markup=main_menu_kb())
        return

    r = random.choice(recipes)
    filtered = [rec for rec in recipes if rec.category == r.category]
    idx = filtered.index(r)
    user_browse_state[message.from_user.id] = {"category": r.category, "index": idx}

    await message.answer(
        f"🎲 Случайный рецепт ({r.category}):",
        reply_markup=nav_kb(),
    )
    await send_recipe(message, r)


@router.callback_query(
    lambda c: c.data
    and c.data.startswith("del:")
    and not c.data.startswith("delc")
)
async def ask_delete(call: CallbackQuery) -> None:
    """Запрашивает подтверждение удаления рецепта."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт не найден", show_alert=True)
        return

    await call.message.edit_reply_markup(reply_markup=delete_confirm_kb(idx))
    await call.answer("Подтвердите удаление")


@router.callback_query(lambda c: c.data and c.data.startswith("delconf:"))
async def confirm_delete(call: CallbackQuery) -> None:
    """Удаляет рецепт после подтверждения."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт уже удалён", show_alert=True)
        return

    title = recipes[idx].title
    delete_recipe(title)

    await call.answer("🗑️ Рецепт удалён!")
    try:
        await call.message.delete()
    except Exception:
        pass


@router.callback_query(lambda c: c.data and c.data.startswith("delcancel:"))
async def cancel_delete(call: CallbackQuery) -> None:
    """Отменяет удаление рецепта и восстанавливает оригинальную клавиатуру."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer()
        return

    recipe = recipes[idx]
    fav = is_favorite(call.from_user.id, recipe.title)
    await call.message.edit_reply_markup(reply_markup=recipe_inline_kb(idx, fav))
    await call.answer("Отменено")


@router.callback_query(lambda c: c.data and c.data.startswith("view:"))
async def view_from_search(call: CallbackQuery) -> None:
    """Открывает рецепт из результатов поиска и устанавливает позицию в его категории."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт не найден", show_alert=True)
        return

    r = recipes[idx]
    filtered = [rec for rec in recipes if rec.category == r.category]
    filter_idx = filtered.index(r)
    user_browse_state[call.from_user.id] = {"category": r.category, "index": filter_idx}

    await call.answer()
    await call.message.answer(
        f"<b>{r.category}</b> — рецепт {filter_idx + 1} из {len(filtered)}:",
        reply_markup=nav_kb(),
    )
    await send_recipe(call.message, r, user_id=call.from_user.id)
