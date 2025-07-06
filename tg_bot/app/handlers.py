from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from .keyboards import *
from .database.db import db
from .utils import *

router = Router()

class StateModule(StatesGroup):
    current_module = State()
    current_theme = State()
    waiting_for_answer = State()

modules_description = {
    1: "description 1",
    2: "description 2",
    3: "description 3",
    4: "description 4",
    5: "description 5",
    6: "description 6",
    7: "description 7",
    8: "description 8",
}



@router.message(Command('start'))
async def start(message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    kb = await get_modules_keyboard(user.id)
    await message.answer('Привет! Я помогу тебе учиться и разбираться в нужных темах.'
                         'Выбери интересующую главу, и я пришлю темы для изучения!', reply_markup=kb)


@router.message(Command('data'))
async def data(message: Message):
    await message.answer('Мы храним следующую информацию о тебе:\n')
    user = await db.get_user_by_id(message.from_user.id)
    if user:
        await message.answer(f"User found: {user}")
    else:
        await message.answer("No data for user")



@router.callback_query(lambda c: c.data in ['module_' + str(i) for i in range(1, 9)])
async def choosing_module(callback_query: CallbackQuery, state: FSMContext):
    selected_module = int(callback_query.data.split('_')[-1])
    await state.update_data(current_module=selected_module)
    await state.update_data(current_theme=1)
    await callback_query.message.answer(modules_description[selected_module])

    post = await db.get_post_by_module_and_theme(selected_module, 1)
    if post:
        await state.update_data(current_theme=1)
        await show_post_with_images(callback_query.message, selected_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! К следующему?',
                                            reply_markup=module_kb)
    await callback_query.answer()
    await callback_query.message.delete()


@router.callback_query(lambda c: c.data == 'next_theme')
async def next_theme_handler(callback_query: CallbackQuery, state: FSMContext):
    gotten_data = await state.get_data()
    current_module = gotten_data.get('current_module')
    current_theme = gotten_data.get('current_theme', 1)

    next_theme = current_theme + 1

    post = await db.get_post_by_module_and_theme(current_module, next_theme)
    if post:
        await state.update_data(current_theme=next_theme)
        await show_post_with_images(callback_query.message, current_module, next_theme, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await db.change_modules_done(callback_query.from_user.id, current_module, "1")

        question = await db.get_question_by_module(current_module)
        if question:
            await callback_query.message.answer(question)
            await state.set_state(StateModule.waiting_for_answer)
        else:
            await callback_query.message.answer('Перейдем к следующему модулю?', reply_markup=module_kb)

    await callback_query.message.delete()


@router.callback_query(lambda c: c.data == 'next_module')
async def next_module_handler(callback_query: CallbackQuery, state: FSMContext):
    gotten_data = await state.get_data()
    current_module = gotten_data.get('current_module')
    next_module = current_module + 1

    if next_module > max(modules_description.keys()):
        await callback_query.message.delete()
        await callback_query.answer()
        await end(callback_query, state)
        return

    await state.update_data(current_theme=1)
    await state.update_data(current_module=next_module)
    await callback_query.message.answer(modules_description[next_module])

    post = await db.get_post_by_module_and_theme(next_module, 1)
    if post:
        await show_post_with_images(callback_query.message, next_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await db.change_modules_done(callback_query.from_user.id, next_module - 1, "1")
        await callback_query.message.answer('Это последняя тема в этом модуле! К следующему?',
                                            reply_markup=module_kb)
    await callback_query.message.delete()



@router.callback_query(lambda c: c.data == 'menu')
async def menu(callback_query: CallbackQuery, state: FSMContext):
    user = callback_query.from_user
    kb = await get_modules_keyboard(user.id)

    await callback_query.message.answer(
        'Выберите интересующий модуль или идите по порядку)', reply_markup=kb)

    await callback_query.message.delete()
    await state.clear()


# ADMIN ONLY
@router.message(Command("add_post"))
async def add_post_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    try:
        _, rest = message.text.split(' ', 1)
        module, theme, title, content = rest.split('|', 3)
        title = title.strip()
        content = content.strip()
    except ValueError:
        await message.answer("Используйте формат: /add_post <номер модуля> | <номер темы> | <заголовок> | <содержимое>")
        return

    post = await db.get_post_by_module_and_theme(int(module), int(theme))
    if post:
        await message.answer("Пост с таким модулем и темой уже существовал, мы его заменили")
        await show_post_with_images(message, int(module), int(theme), db)
        await message.answer("Поста сверху больше не существует.")
        return

    post_id = await db.add_post(user_id=message.from_user.id, module=int(module), theme=int(theme), title=title, content=content)
    await message.answer(f"Пост добавлен с id = {post_id}")


# ADMIN ONLY
@router.message(Command("add_image"))
async def add_image_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    try:
        if ' ' not in message.text:
            raise ValueError("Нет аргументов")
        _, rest = message.text.split(' ', 1)
        parts = [p.strip() for p in rest.split('|', maxsplit=2)]
        if len(parts) != 3:
            raise ValueError("Неверное количество аргументов")
        module = int(parts[0])
        theme = int(parts[1])
        image_url = parts[2]
    except (ValueError, IndexError):
        await message.answer("Используйте формат:\n/add_image <номер модуля> | <номер темы> | <URL картинки>")
        return

    post = await db.get_post_by_module_and_theme(module, theme)
    if not post:
        await message.answer("Пост с таким модулем и темой не найден.")
        return

    await db.add_image_to_post(post_id=post['id'], image_url=image_url)
    await message.answer("Картинка успешно добавлена к посту.")

# ADMIN ONLY
@router.message(Command("add_question"))
async def add_question_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    try:
        if ' ' not in message.text:
            raise ValueError("Нет аргументов")
        _, rest = message.text.split(' ', 1)
        parts = [p.strip() for p in rest.split('|', maxsplit=1)]
        if len(parts) != 2:
            raise ValueError("Неверное количество аргументов")
        module = int(parts[0])
        question = parts[1]
    except (ValueError, IndexError):
        await message.answer("Используйте формат:\n/add_question <номер модуля> | <вопрос>")
        return

    await db.add_question(module, question)
    await message.answer("Вопрос к модулю успешно добавлен")


@router.message(StateModule.waiting_for_answer)
async def handle_module_answer(message: Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    current_module = data.get('current_module')

    await db.save_answer(user_id=message.from_user.id, module=current_module, answer=user_answer)

    await message.answer("Спасибо за ответ! Переходим к следующему модулю?", reply_markup=module_kb)

    await state.update_data(current_theme=1)
    await state.set_state(StateModule.current_module)



async def end(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Конец')
    await state.clear()
