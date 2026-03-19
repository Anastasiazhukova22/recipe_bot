import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv

from handlers import view_recipes, add_recipe, search, favorites, categories, edit_recipe
from keyboards.main import main_menu_kb

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Создайте файл .env и добавьте BOT_TOKEN=<ваш токен>")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def main() -> None:
    """Инициализирует и запускает бота."""
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(edit_recipe.router)
    dp.include_router(add_recipe.router)
    dp.include_router(search.router)
    dp.include_router(favorites.router)
    dp.include_router(categories.router)
    dp.include_router(view_recipes.router)

    @dp.message(F.text == "/start")
    async def cmd_start(message: Message) -> None:
        """Приветствует пользователя и показывает главное меню."""
        name = message.from_user.first_name or "друг"
        await message.answer(
            f"Привет, <b>{name}</b>! 👋\n\n"
            "Я бот для хранения и поиска рецептов 🍽️\n\n"
            "<b>Что я умею:</b>\n"
            "📖 Листать рецепты по категориям\n"
            "🔍 Искать по названию или ингредиенту\n"
            "⭐ Сохранять избранные рецепты\n"
            "🎲 Предлагать случайный рецепт\n"
            "➕ Добавлять новые рецепты с фото\n"
            "✏️ Редактировать любое поле рецепта\n\n"
            "Выберите действие в меню 👇",
            reply_markup=main_menu_kb(),
        )

    @dp.message(F.text == "/help")
    async def cmd_help(message: Message) -> None:
        """Отправляет справку по функциям бота."""
        await message.answer(
            "<b>📋 Справка</b>\n\n"
            "<b>📖 Рецепты</b> — выберите категорию и листайте рецепты кнопками ⬅️ ➡️\n\n"
            "<b>🔍 Поиск</b> — введите слово из названия или списка ингредиентов\n\n"
            "<b>⭐ Избранное</b> — нажмите ⭐ под рецептом, чтобы сохранить. "
            "Доступно через кнопку ⭐ Избранное в меню.\n\n"
            "<b>🎲 Случайный</b> — получите случайный рецепт и листайте его категорию\n\n"
            "<b>➕ Добавить рецепт</b> — пошаговое добавление с фото, временем и сложностью\n\n"
            "<b>✏️ Редактирование</b> — нажмите ✏️ Изменить под рецептом и выберите поле\n\n"
            "<b>🗑️ Удалить рецепт</b> — нажмите кнопку удаления под рецептом и подтвердите\n\n"
            "<b>📂 Категории</b> — создавайте свои категории для рецептов",
            reply_markup=main_menu_kb(),
        )

    @dp.message(F.text == "🏠 Меню")
    async def show_menu(message: Message) -> None:
        """Показывает главное меню."""
        await message.answer("Главное меню:", reply_markup=main_menu_kb())

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать / Главное меню"),
        BotCommand(command="help", description="Справка по боту"),
    ])

    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
