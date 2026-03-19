from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from data import recipes, categories, DEFAULT_CATEGORIES, DIFFICULTIES, COOK_TIMES


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Главное меню с основными разделами бота."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Рецепты"), KeyboardButton(text="🔍 Поиск")],
            [KeyboardButton(text="⭐ Избранное"), KeyboardButton(text="🎲 Случайный")],
            [KeyboardButton(text="➕ Добавить рецепт"), KeyboardButton(text="📂 Категории")],
        ],
        resize_keyboard=True,
    )


def categories_kb(allow_create: bool = False) -> ReplyKeyboardMarkup:
    """Кнопки категорий с количеством рецептов в каждой.
    allow_create=True добавляет кнопку создания новой категории (для добавления рецепта)."""
    buttons = []
    for cat in categories:
        count = sum(1 for r in recipes if r.category == cat)
        buttons.append([KeyboardButton(text=f"{cat} ({count})")])
    if allow_create:
        buttons.append([KeyboardButton(text="✏️ Создать категорию")])
    buttons.append([KeyboardButton(text="🏠 Меню")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def nav_kb() -> ReplyKeyboardMarkup:
    """Клавиатура навигации по рецептам."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="➡️ Вперёд")],
            [KeyboardButton(text="🏠 Меню")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    """Клавиатура с единственной кнопкой отмены."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def recipe_inline_kb(recipe_idx: int, is_fav: bool) -> InlineKeyboardMarkup:
    """Inline-клавиатура рецепта: избранное, редактирование, удаление."""
    fav_text = "💛 В избранном" if is_fav else "⭐ В избранное"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=fav_text, callback_data=f"fav:{recipe_idx}"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit:{recipe_idx}"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"del:{recipe_idx}"),
            ],
        ]
    )


def delete_confirm_kb(recipe_idx: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура подтверждения удаления рецепта."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить", callback_data=f"delconf:{recipe_idx}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data=f"delcancel:{recipe_idx}"
                ),
            ]
        ]
    )


def search_results_kb(indices: list[int], titles: list[str]) -> InlineKeyboardMarkup:
    """Inline-клавиатура со списком результатов поиска."""
    buttons = [
        [InlineKeyboardButton(text=t, callback_data=f"view:{i}")]
        for i, t in zip(indices, titles)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_kb(edit_mode: bool = False) -> ReplyKeyboardMarkup:
    """Reply-клавиатура выбора времени приготовления."""
    rows = [
        [KeyboardButton(text=COOK_TIMES[i]), KeyboardButton(text=COOK_TIMES[i + 1])]
        for i in range(0, len(COOK_TIMES) - 1, 2)
    ]
    if len(COOK_TIMES) % 2:
        rows.append([KeyboardButton(text=COOK_TIMES[-1])])
    bottom = "🗑️ Убрать" if edit_mode else "⏭️ Пропустить"
    rows.append([KeyboardButton(text=bottom)])
    rows.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def difficulty_kb(edit_mode: bool = False) -> ReplyKeyboardMarkup:
    """Reply-клавиатура выбора сложности."""
    bottom = "🗑️ Убрать" if edit_mode else "⏭️ Пропустить"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=d) for d in DIFFICULTIES],
            [KeyboardButton(text=bottom)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def edit_field_kb(recipe_idx: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура выбора поля для редактирования."""
    p = recipe_idx
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Название",      callback_data=f"editfield:{p}:title"),
                InlineKeyboardButton(text="📂 Категория",   callback_data=f"editfield:{p}:category"),
            ],
            [
                InlineKeyboardButton(text="🥗 Ингредиенты",  callback_data=f"editfield:{p}:ingredients"),
                InlineKeyboardButton(text="👨‍🍳 Шаги",       callback_data=f"editfield:{p}:steps"),
            ],
            [
                InlineKeyboardButton(text="⏱️ Время",         callback_data=f"editfield:{p}:cook_time"),
                InlineKeyboardButton(text="📊 Сложность",   callback_data=f"editfield:{p}:difficulty"),
            ],
            [
                InlineKeyboardButton(text="📷 Фото",          callback_data=f"editfield:{p}:image"),
            ],
        ]
    )


def manage_categories_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура управления категориями: удаление пользовательских + создание."""
    buttons = []
    for cat in categories:
        if cat not in DEFAULT_CATEGORIES:
            count = sum(1 for r in recipes if r.category == cat)
            label = f"🗑️ {cat} ({count})" if count else f"🗑️ {cat}"
            buttons.append([InlineKeyboardButton(text=label, callback_data=f"catdel:{cat}")])
    buttons.append([InlineKeyboardButton(text="➕ Создать категорию", callback_data="catadd")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
