from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import search_recipes, recipes
from keyboards.main import cancel_kb, search_results_kb, main_menu_kb

router = Router()


class SearchRecipe(StatesGroup):
    """FSM-состояния диалога поиска рецепта."""

    query = State()


@router.message(F.text == "🔍 Поиск")
async def start_search(message: Message, state: FSMContext) -> None:
    """Запускает диалог поиска рецепта."""
    await state.clear()
    await state.set_state(SearchRecipe.query)
    await message.answer(
        "🔍 Введите название блюда или ингредиент:",
        reply_markup=cancel_kb(),
    )


@router.message(F.text == "❌ Отмена", StateFilter(SearchRecipe))
async def cancel_search(message: Message, state: FSMContext) -> None:
    """Отменяет поиск и возвращает в главное меню."""
    await state.clear()
    await message.answer("Поиск отменён.", reply_markup=main_menu_kb())


@router.message(SearchRecipe.query)
async def process_search(message: Message, state: FSMContext) -> None:
    """Обрабатывает запрос и отображает найденные рецепты."""
    query = (message.text or "").strip()
    await state.clear()

    if not query:
        await message.answer("Запрос не может быть пустым.", reply_markup=main_menu_kb())
        return

    results = search_recipes(query)

    if not results:
        await message.answer(
            f"По запросу <b>«{query}»</b> ничего не найдено 😔\n"
            "Попробуйте другой запрос.",
            reply_markup=main_menu_kb(),
        )
        return

    indices = [recipes.index(r) for r in results]
    titles = [r.title for r in results]

    await message.answer(
        f"🔍 Найдено рецептов: <b>{len(results)}</b>\nВыберите, чтобы открыть:",
        reply_markup=search_results_kb(indices, titles),
    )
    await message.answer("После выбора рецепта можно листать всю категорию ⬅️ ➡️", reply_markup=main_menu_kb())
