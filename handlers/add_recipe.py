from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import recipes, Recipe, save_recipes, add_category, COOK_TIMES, DIFFICULTIES
from keyboards.main import categories_kb, main_menu_kb, cancel_kb, time_kb, difficulty_kb

router = Router()


class AddRecipe(StatesGroup):
    """FSM-состояния диалога добавления рецепта."""

    title = State()
    category = State()
    new_category_name = State()
    ingredients = State()
    steps = State()
    cook_time = State()
    difficulty = State()
    image = State()


@router.message(F.text == "❌ Отмена", StateFilter(AddRecipe))
async def cancel_add(message: Message, state: FSMContext) -> None:
    """Отменяет процесс добавления рецепта."""
    await state.clear()
    await message.answer("❌ Добавление отменено.", reply_markup=main_menu_kb())


@router.message(F.text == "➕ Добавить рецепт")
async def start_add_recipe(message: Message, state: FSMContext) -> None:
    """Запускает диалог добавления рецепта."""
    await state.clear()
    await state.set_state(AddRecipe.title)
    await message.answer(
        "📝 Введите название рецепта:\n\n"
        "<i>Нажмите ❌ Отмена чтобы прервать добавление.</i>",
        reply_markup=cancel_kb(),
    )


@router.message(AddRecipe.title)
async def add_title(message: Message, state: FSMContext) -> None:
    """Принимает название рецепта."""
    if not message.text or not message.text.strip():
        await message.answer("Название не может быть пустым. Введите ещё раз:")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddRecipe.category)
    await message.answer("📂 Выберите категорию:", reply_markup=categories_kb(allow_create=True))


@router.message(AddRecipe.category)
async def add_category_step(message: Message, state: FSMContext) -> None:
    """Принимает выбор категории или запускает создание новой."""
    raw = message.text or ""

    if raw == "✏️ Создать категорию":
        await state.set_state(AddRecipe.new_category_name)
        await message.answer(
            "✏️ Введите название новой категории:",
            reply_markup=cancel_kb(),
        )
        return

    from data import categories
    matched = next((c for c in categories if raw == c or raw.startswith(f"{c} (")), None)
    if not matched:
        await message.answer("Выберите категорию из списка 👇", reply_markup=categories_kb(allow_create=True))
        return
    await state.update_data(category=matched)
    await state.set_state(AddRecipe.ingredients)
    await message.answer(
        "🥗 Перечислите ингредиенты (можно через запятую или каждый с новой строки):",
        reply_markup=cancel_kb(),
    )


@router.message(AddRecipe.new_category_name)
async def add_new_category_name(message: Message, state: FSMContext) -> None:
    """Создаёт новую категорию и переходит к вводу ингредиентов."""
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым. Введите ещё раз:")
        return

    added = add_category(name)
    display = f"✅ Категория <b>{name}</b> создана!" if added else f"ℹ️ Категория <b>{name}</b> уже существует."

    await state.update_data(category=name)
    await state.set_state(AddRecipe.ingredients)
    await message.answer(
        f"{display}\n\n🥗 Перечислите ингредиенты:",
        reply_markup=cancel_kb(),
    )


@router.message(AddRecipe.ingredients)
async def add_ingredients(message: Message, state: FSMContext) -> None:
    """Принимает список ингредиентов."""
    await state.update_data(ingredients=message.text)
    await state.set_state(AddRecipe.steps)
    await message.answer("👨‍🍳 Опишите шаги приготовления:", reply_markup=cancel_kb())


@router.message(AddRecipe.steps)
async def add_steps(message: Message, state: FSMContext) -> None:
    """Принимает шаги приготовления."""
    await state.update_data(steps=message.text)
    await state.set_state(AddRecipe.cook_time)
    await message.answer(
        "⏱️ Укажите время приготовления или нажмите <b>⏭️ Пропустить</b>:",
        reply_markup=time_kb(),
    )


@router.message(AddRecipe.cook_time)
async def add_cook_time(message: Message, state: FSMContext) -> None:
    """Принимает время приготовления или пропуск этого шага."""
    raw = (message.text or "").strip()
    if raw == "⏭️ Пропустить":
        await state.update_data(cook_time=None)
    elif raw in COOK_TIMES:
        await state.update_data(cook_time=raw)
    else:
        await message.answer("Выберите вариант из списка 👇", reply_markup=time_kb())
        return
    await state.set_state(AddRecipe.difficulty)
    await message.answer(
        "📊 Укажите сложность или нажмите <b>⏭️ Пропустить</b>:",
        reply_markup=difficulty_kb(),
    )


@router.message(AddRecipe.difficulty)
async def add_difficulty(message: Message, state: FSMContext) -> None:
    """Принимает сложность рецепта или пропуск этого шага."""
    raw = (message.text or "").strip()
    if raw == "⏭️ Пропустить":
        await state.update_data(difficulty=None)
    elif raw in DIFFICULTIES:
        await state.update_data(difficulty=raw)
    else:
        await message.answer("Выберите вариант из списка 👇", reply_markup=difficulty_kb())
        return
    await state.set_state(AddRecipe.image)
    await message.answer(
        "📷 Пришлите фото блюда или напишите «нет»:",
        reply_markup=cancel_kb(),
    )


@router.message(AddRecipe.image)
async def add_image(message: Message, state: FSMContext) -> None:
    """Принимает фото рецепта и сохраняет новый рецепт."""
    image: str | None = None
    if message.photo:
        image = message.photo[-1].file_id
    elif message.text and message.text.strip().lower() == "нет":
        image = None
    else:
        await message.answer("Отправь фото или напиши «нет»:")
        return

    data = await state.get_data()
    recipes.append(
        Recipe(
            title=data["title"],
            category=data["category"],
            ingredients=data["ingredients"],
            steps=data["steps"],
            cook_time=data.get("cook_time"),
            difficulty=data.get("difficulty"),
            image=image,
        )
    )
    save_recipes(recipes)
    await state.clear()
    await message.answer(
        f"✅ Рецепт <b>{data['title']}</b> добавлен!",
        reply_markup=main_menu_kb(),
    )
