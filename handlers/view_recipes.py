from aiogram import Router
from aiogram.types import Message

from data import recipes, user_recipe_index
from keyboards.main import categories_kb, nav_kb

router = Router()


@router.message(lambda m: m.text == "📖 Рецепты")
async def choose_category(message: Message):
    await message.answer(
        "Выберите категорию:",
        reply_markup=categories_kb()
    )


@router.message(lambda m: m.text in {r.category for r in recipes})
async def show_first(message: Message):
    user_recipe_index[message.from_user.id] = 0
    await show_recipe(message, message.text)


@router.message(lambda m: m.text == "➡️ Вперёд")
async def next_recipe(message: Message):
    user_id = message.from_user.id
    user_recipe_index[user_id] = user_recipe_index.get(user_id, 0) + 1

    category = message.reply_to_message.text.split("\n")[0]
    await show_recipe(message, category)


async def show_recipe(message: Message, category: str):
    index = user_recipe_index.get(message.from_user.id, 0)

    filtered = [r for r in recipes if r.category == category]
    if not filtered:
        await message.answer("В этой категории пока нет рецептов")
        return

    if index >= len(filtered):
        index = 0

    r = filtered[index]

    text = (
        f"<b>{r.title}</b>\n\n"
        f"<b>Ингредиенты:</b>\n{r.ingredients}\n\n"
        f"<b>Приготовление:</b>\n{r.steps}"
    )

    user_recipe_index[message.from_user.id] = index

    # 🔴 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ
    if isinstance(r.image, str) and r.image.startswith(("http://", "https://")):
        await message.answer_photo(
            photo=r.image,
            caption=text,
            reply_markup=nav_kb()
        )
    else:
        await message.answer(
            text,
            reply_markup=nav_kb()
        )