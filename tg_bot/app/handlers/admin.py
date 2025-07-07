from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..database.db import db
from ..utils import *

router = Router()



# ADMIN ONLY: Handler для добавления нового поста
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

# ADMIN ONLY: Handler для добавления картинки к посту
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

# ADMIN ONLY: Handler для добавления вопроса к модулю
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