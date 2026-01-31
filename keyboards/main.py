from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Рецепты")],
            [KeyboardButton(text="➕ Добавить рецепт")]
        ],
        resize_keyboard=True
    )


def categories_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in ["Завтрак", "Обед", "Ужин", "Десерт"]],
        resize_keyboard=True
    )


def nav_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="➡️ Вперёд")],
            [KeyboardButton(text="🏠 Меню")]
        ],
        resize_keyboard=True
    )
