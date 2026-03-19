from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data import recipes, save_recipes, categories, add_category, COOK_TIMES, DIFFICULTIES
from keyboards.main import (
    main_menu_kb, cancel_kb, edit_field_kb,
    categories_kb, time_kb, difficulty_kb,
)
from handlers.common import send_recipe

router = Router()

FIELD_LABELS = {
    "title":       "🏷️ Название",
    "category":    "📂 Категория",
    "ingredients": "🥗 Ингредиенты",
    "steps":       "👨‍🍳 Шаги приготовления",
    "cook_time":   "⏱️ Время",
    "difficulty":  "📊 Сложность",
    "image":       "📷 Фото",
}


class EditRecipe(StatesGroup):
    """FSM-состояния диалога редактирования рецепта."""

    editing_title       = State()
    editing_category    = State()
    editing_new_category = State()
    editing_ingredients = State()
    editing_steps       = State()
    editing_cook_time   = State()
    editing_difficulty  = State()
    editing_image       = State()


@router.message(F.text == "❌ Отмена", StateFilter(EditRecipe))
async def cancel_edit(message: Message, state: FSMContext) -> None:
    """Отменяет редактирование рецепта."""
    await state.clear()
    await message.answer("✏️ Редактирование отменено.", reply_markup=main_menu_kb())


@router.callback_query(lambda c: c.data and c.data.startswith("edit:") and "field" not in c.data)
async def open_edit_menu(call: CallbackQuery) -> None:
    """Открывает меню выбора поля для редактирования."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт не найден", show_alert=True)
        return

    r = recipes[idx]
    await call.answer()
    await call.message.answer(
        f"✏️ <b>Редактирование: {r.title}</b>\n\nВыберите поле:",
        reply_markup=edit_field_kb(idx),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("editfield:"))
async def choose_field(call: CallbackQuery, state: FSMContext) -> None:
    """Обрабатывает выбор поля и переводит в соответствующее FSM-состояние."""
    _, raw_idx, field = call.data.split(":", 2)
    idx = int(raw_idx)

    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт не найден", show_alert=True)
        return

    await state.update_data(recipe_idx=idx)
    await call.answer()

    r = recipes[idx]
    label = FIELD_LABELS.get(field, field)

    if field == "title":
        await state.set_state(EditRecipe.editing_title)
        await call.message.answer(
            f"{label}  →  сейчас: <b>{r.title}</b>\n\nВведите новое название:",
            reply_markup=cancel_kb(),
        )

    elif field == "category":
        await state.set_state(EditRecipe.editing_category)
        await call.message.answer(
            f"{label}  →  сейчас: <b>{r.category}</b>\n\nВыберите новую категорию:",
            reply_markup=categories_kb(allow_create=True),
        )

    elif field == "ingredients":
        await state.set_state(EditRecipe.editing_ingredients)
        await call.message.answer(
            f"{label}  →  сейчас:\n{r.ingredients}\n\nВведите новый список:",
            reply_markup=cancel_kb(),
        )

    elif field == "steps":
        await state.set_state(EditRecipe.editing_steps)
        await call.message.answer(
            f"{label}  →  сейчас:\n{r.steps}\n\nВведите новые шаги:",
            reply_markup=cancel_kb(),
        )

    elif field == "cook_time":
        current = r.cook_time or "—"
        await state.set_state(EditRecipe.editing_cook_time)
        await call.message.answer(
            f"{label}  →  сейчас: <b>{current}</b>\n\nВыберите новое время или нажмите 🗑️ Убрать:",
            reply_markup=time_kb(edit_mode=True),
        )

    elif field == "difficulty":
        current = r.difficulty or "—"
        await state.set_state(EditRecipe.editing_difficulty)
        await call.message.answer(
            f"{label}  →  сейчас: <b>{current}</b>\n\nВыберите сложность или нажмите 🗑️ Убрать:",
            reply_markup=difficulty_kb(edit_mode=True),
        )

    elif field == "image":
        await state.set_state(EditRecipe.editing_image)
        has_img = "есть" if r.image else "нет"
        await call.message.answer(
            f"{label}  →  сейчас: <b>{has_img}</b>\n\n"
            "Пришлите новое фото, «нет» чтобы убрать, или «оставить» для сохранения текущего:",
            reply_markup=cancel_kb(),
        )


async def _save_and_confirm(message: Message, state: FSMContext, idx: int) -> None:
    """Сохраняет изменения, сбрасывает FSM-состояние и отображает обновлённый рецепт."""
    save_recipes(recipes)
    await state.clear()
    await message.answer("✅ Рецепт обновлён!", reply_markup=main_menu_kb())
    await send_recipe(message, recipes[idx])


@router.message(EditRecipe.editing_title)
async def process_title(message: Message, state: FSMContext) -> None:
    """Сохраняет новое название рецепта."""
    val = (message.text or "").strip()
    if not val:
        await message.answer("Название не может быть пустым:")
        return
    data = await state.get_data()
    recipes[data["recipe_idx"]].title = val
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_category)
async def process_category(message: Message, state: FSMContext) -> None:
    """Сохраняет выбранную категорию рецепта."""
    raw = message.text or ""

    if raw == "✏️ Создать категорию":
        await state.set_state(EditRecipe.editing_new_category)
        await message.answer("✏️ Введите название новой категории:", reply_markup=cancel_kb())
        return

    matched = next((c for c in categories if raw == c or raw.startswith(f"{c} (")), None)
    if not matched:
        await message.answer("Выберите категорию из списка 👇", reply_markup=categories_kb(allow_create=True))
        return

    data = await state.get_data()
    recipes[data["recipe_idx"]].category = matched
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_new_category)
async def process_new_category(message: Message, state: FSMContext) -> None:
    """Создаёт новую категорию и присваивает её рецепту."""
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым:")
        return
    add_category(name)
    data = await state.get_data()
    recipes[data["recipe_idx"]].category = name
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_ingredients)
async def process_ingredients(message: Message, state: FSMContext) -> None:
    """Сохраняет новый список ингредиентов."""
    data = await state.get_data()
    recipes[data["recipe_idx"]].ingredients = message.text or ""
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_steps)
async def process_steps(message: Message, state: FSMContext) -> None:
    """Сохраняет новые шаги приготовления."""
    data = await state.get_data()
    recipes[data["recipe_idx"]].steps = message.text or ""
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_cook_time)
async def process_cook_time(message: Message, state: FSMContext) -> None:
    """Сохраняет новое время приготовления."""
    raw = (message.text or "").strip()
    if raw == "🗑️ Убрать":
        new_val = None
    elif raw in COOK_TIMES:
        new_val = raw
    else:
        await message.answer("Выберите вариант из списка 👇", reply_markup=time_kb(edit_mode=True))
        return
    data = await state.get_data()
    recipes[data["recipe_idx"]].cook_time = new_val
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_difficulty)
async def process_difficulty(message: Message, state: FSMContext) -> None:
    """Сохраняет новую сложность."""
    raw = (message.text or "").strip()
    if raw == "🗑️ Убрать":
        new_val = None
    elif raw in DIFFICULTIES:
        new_val = raw
    else:
        await message.answer("Выберите вариант из списка 👇", reply_markup=difficulty_kb(edit_mode=True))
        return
    data = await state.get_data()
    recipes[data["recipe_idx"]].difficulty = new_val
    await _save_and_confirm(message, state, data["recipe_idx"])


@router.message(EditRecipe.editing_image)
async def process_image(message: Message, state: FSMContext) -> None:
    """Сохраняет новое фото рецепта или убирает существующее."""
    data = await state.get_data()
    idx = data["recipe_idx"]
    raw = (message.text or "").strip().lower()

    if message.photo:
        recipes[idx].image = message.photo[-1].file_id
    elif raw == "нет":
        recipes[idx].image = None
    elif raw == "оставить":
        pass  # ничего не меняем
    else:
        await message.answer(
            "Пришлите фото, «нет» чтобы убрать, или «оставить» для сохранения текущего:"
        )
        return

    await _save_and_confirm(message, state, idx)
