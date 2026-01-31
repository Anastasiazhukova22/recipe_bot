from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Рецепты", callback_data="recipes")],
            [InlineKeyboardButton(text="➕ Добавить рецепт", callback_data="add_recipe")]
        ]
    )


def recipe_nav():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data="prev"),
                InlineKeyboardButton(text="➡️", callback_data="next"),
            ]
        ]
    )


def categories_menu(categories: list[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=c, callback_data=f"cat:{c}")]
            for c in categories
        ]
    )
