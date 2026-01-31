from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import recipes, Recipe, save_recipes
from keyboards.main import categories_kb, main_menu_kb

router = Router()


class AddRecipe(StatesGroup):
    title = State()
    category = State()
    ingredients = State()
    steps = State()
    image = State()


@router.message(lambda m: m.text == "➕ Добавить рецепт")
async def start_add_recipe(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddRecipe.title)
    await message.answer("Название рецепта?")


@router.message(AddRecipe.title)
async def add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddRecipe.category)
    await message.answer("Категория:", reply_markup=categories_kb())


@router.message(AddRecipe.category)
async def add_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddRecipe.ingredients)
    await message.answer("Ингредиенты:")


@router.message(AddRecipe.ingredients)
async def add_ingredients(message: Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await state.set_state(AddRecipe.steps)
    await message.answer("Шаги приготовления:")

@router.message(AddRecipe.steps)
async def add_steps(message: Message, state: FSMContext):
    await state.update_data(steps=message.text)
    await state.set_state(AddRecipe.image)
    await message.answer("Пришли фото блюда или напиши «нет»")


@router.message(AddRecipe.image)
async def add_image(message: Message, state: FSMContext):
    data = await state.get_data()

    image = None
    if message.photo:
        image = message.photo[-1].file_id
    elif message.text and message.text.lower() != "нет":
        await message.answer("Отправь фото или напиши «нет»")
        return

    recipes.append(
        Recipe(
            title=data["title"],
            category=data["category"],
            ingredients=data["ingredients"],
            steps=data["steps"],
            image=image
        )
    )

    save_recipes(recipes)

    await state.clear()
    await message.answer("✅ Рецепт добавлен", reply_markup=main_menu_kb())