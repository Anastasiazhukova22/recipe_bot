import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from handlers import view_recipes, add_recipe
from keyboards.main import main_menu_kb

TOKEN = "8566528753:AAG6UYpDMnnqPkrQqC5rVaM0taTjf9KXUQU"


async def main():
    bot = Bot(
        TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # роутеры
    dp.include_router(add_recipe.router)
    dp.include_router(view_recipes.router)

    # ===== /start =====
    @dp.message(F.text == "/start")
    async def cmd_start(message: Message):
        await message.answer(
            "Меню:",
            reply_markup=main_menu_kb()
        )

    # ===== кнопка Меню =====
    @dp.message(F.text == "🏠 Меню")
    async def show_menu(message: Message):
        await message.answer(
            "Меню:",
            reply_markup=main_menu_kb()
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())