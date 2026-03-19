from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data import categories, DEFAULT_CATEGORIES, recipes, add_category, delete_category
from keyboards.main import main_menu_kb, cancel_kb, manage_categories_inline_kb

router = Router()


class CreateCategory(StatesGroup):
    """FSM-состояния диалога создания категории."""

    name = State()


def _categories_text() -> str:
    """Формирует HTML-текст со списком категорий и количеством рецептов в каждой."""
    lines = []
    for cat in categories:
        count = sum(1 for r in recipes if r.category == cat)
        badge = "🔒" if cat in DEFAULT_CATEGORIES else "✏️"
        noun = "рецептов" if count in (0, 5, 6, 7, 8, 9, 11, 12) else ("рецепт" if count == 1 else "рецепта")
        lines.append(f"{badge} <b>{cat}</b> — {count} {noun}")
    return (
        "📂 <b>Категории рецептов</b>\n\n"
        + "\n".join(lines)
        + "\n\n🔒 — встроенная   ✏️ — пользовательская\n\n"
        "<i>Нажмите 🗑️ чтобы удалить пользовательскую категорию,\n"
        "или ➕ чтобы создать новую.</i>"
    )


@router.message(F.text == "📂 Категории")
async def show_categories(message: Message) -> None:
    """Показывает список категорий с кнопками управления."""
    await message.answer(_categories_text(), reply_markup=manage_categories_inline_kb())


@router.callback_query(F.data == "catadd")
async def start_create_category(call: CallbackQuery, state: FSMContext) -> None:
    """Запускает диалог создания новой категории."""
    await state.set_state(CreateCategory.name)
    await call.answer()
    await call.message.answer(
        "✏️ Введите название новой категории:",
        reply_markup=cancel_kb(),
    )


@router.message(F.text == "❌ Отмена", StateFilter(CreateCategory))
async def cancel_create(message: Message, state: FSMContext) -> None:
    """Отменяет создание категории."""
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu_kb())


@router.message(CreateCategory.name)
async def process_create_category(message: Message, state: FSMContext) -> None:
    """Создаёт категорию с введённым названием."""
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым. Введите ещё раз:")
        return

    added = add_category(name)
    await state.clear()

    if added:
        text = f"✅ Категория <b>{name}</b> создана! Теперь можно добавлять в неё рецепты."
    else:
        text = f"⚠️ Категория <b>{name}</b> уже существует."

    await message.answer(text, reply_markup=main_menu_kb())
    await message.answer(_categories_text(), reply_markup=manage_categories_inline_kb())


@router.callback_query(lambda c: c.data and c.data.startswith("catdel:"))
async def delete_category_cb(call: CallbackQuery) -> None:
    """Обрабатывает запрос на удаление пользовательской категории."""
    name = call.data.split(":", 1)[1]
    success, reason = delete_category(name)

    if not success:
        if reason == "default":
            await call.answer("Встроенные категории нельзя удалить 🔒", show_alert=True)
        elif reason.startswith("has_recipes:"):
            count = reason.split(":")[1]
            await call.answer(
                f"Нельзя удалить: в категории {count} рец.\n"
                "Сначала удалите или переместите рецепты.",
                show_alert=True,
            )
        else:
            await call.answer("Категория не найдена", show_alert=True)
        return

    await call.answer(f"✅ Категория «{name}» удалена")
    try:
        await call.message.edit_text(
            _categories_text(), reply_markup=manage_categories_inline_kb()
        )
    except Exception:
        pass
