from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from data import get_favorites, user_browse_state, recipes, toggle_favorite, is_favorite
from keyboards.main import nav_kb, main_menu_kb, recipe_inline_kb
from handlers.common import send_recipe

router = Router()


@router.message(F.text == "⭐ Избранное")
async def show_favorites(message: Message) -> None:
    """Показывает первый рецепт из избранного пользователя."""
    user_id = message.from_user.id
    favs = get_favorites(user_id)

    if not favs:
        await message.answer(
            "У вас пока нет избранных рецептов 😔\n\n"
            "Нажмите <b>⭐ В избранное</b> под любым рецептом, чтобы сохранить его.",
            reply_markup=main_menu_kb(),
        )
        return

    user_browse_state[user_id] = {"category": "__favorites__", "index": 0}

    await message.answer(
        f"⭐ Избранное — рецепт 1 из {len(favs)}:",
        reply_markup=nav_kb(),
    )
    await send_recipe(message, favs[0], user_id=user_id)


@router.callback_query(lambda c: c.data and c.data.startswith("fav:"))
async def toggle_fav(call: CallbackQuery) -> None:
    """Добавляет или убирает рецепт из избранного и обновляет клавиатуру."""
    idx = int(call.data.split(":")[1])
    if idx < 0 or idx >= len(recipes):
        await call.answer("Рецепт не найден", show_alert=True)
        return

    recipe = recipes[idx]
    added = toggle_favorite(call.from_user.id, recipe.title)
    fav = is_favorite(call.from_user.id, recipe.title)

    await call.message.edit_reply_markup(reply_markup=recipe_inline_kb(idx, fav))
    await call.answer("⭐ Добавлено в избранное!" if added else "💔 Убрано из избранного")
