"""Общие утилиты: отправка карточки рецепта."""
from pathlib import Path

from aiogram.types import Message, FSInputFile

from data import recipes, is_favorite, Recipe
from keyboards.main import recipe_inline_kb


async def send_recipe(
    message: Message,
    recipe: Recipe,
    user_id: int | None = None,
) -> None:
    """Отправляет карточку рецепта с фото (если есть) и inline-кнопками."""
    uid = user_id if user_id is not None else message.from_user.id

    fav = is_favorite(uid, recipe.title)
    try:
        global_idx = recipes.index(recipe)
    except ValueError:
        global_idx = 0

    inline = recipe_inline_kb(global_idx, fav)

    meta = f"<i>{recipe.category}</i>"
    if recipe.cook_time:
        meta += f"  •  ⏱️ {recipe.cook_time}"
    if recipe.difficulty:
        meta += f"  •  {recipe.difficulty}"

    text = (
        f"<b>{recipe.title}</b>  •  {meta}\n\n"
        f"<b>🥗 Ингредиенты:</b>\n{recipe.ingredients}\n\n"
        f"<b>👨‍🍳 Приготовление:</b>\n{recipe.steps}"
    )

    img = recipe.image
    if img:
        if img.startswith(("http://", "https://")):
            await message.answer_photo(photo=img, caption=text, reply_markup=inline)
            return
        path = Path(img)
        if path.exists():
            await message.answer_photo(
                photo=FSInputFile(path), caption=text, reply_markup=inline
            )
            return

    await message.answer(text, reply_markup=inline)
