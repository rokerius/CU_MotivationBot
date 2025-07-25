from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram.types.input_file import FSInputFile, InputFile

from ..database.db import db
from ..database.db_utils import dicts_to_csv
from ..utils import *

router = Router()



# ADMIN ONLY: Handler для добавления нового поста
@router.message(Command("set_post"))
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
        await message.answer("Используйте формат: /set_post <номер модуля> | <номер темы> | <заголовок> | <содержимое>")
        return

    existing_post = await db.get_post_by_module_and_theme(int(module), int(theme))
    if existing_post:
        await message.answer("Пост с таким модулем и темой уже существовал, мы его заменили")
        await show_post_with_images(message, int(module), int(theme), db)
        await message.answer("Поста сверху больше не существует.")

    post_id = await db.add_post(user_id=message.from_user.id, module=int(module),
                                theme=int(theme), title=title, content=content)
    await message.answer(f"Пост добавлен с id = {post_id}")

# ADMIN ONLY: Handler для добавления картинки к посту
@router.message(Command("set_image"))
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
        await message.answer("Используйте формат:\n/set_image <номер модуля> | <номер темы> | <URL картинки>")
        return

    post = await db.get_post_by_module_and_theme(module, theme)
    if not post:
        await message.answer("Пост с таким модулем и темой не найден.")
        return

    await db.add_image_to_post(post_id=post['id'], image_url=image_url)
    await message.answer("Картинка успешно добавлена к посту.")

# ADMIN ONLY: Handler для добавления вопроса к модулю
@router.message(Command("set_question"))
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
        await message.answer("Используйте формат:\n/set_question <номер модуля> | <вопрос>")
        return

    await db.add_question(module, question)
    await message.answer("Вопрос к модулю успешно добавлен")


@router.message(Command("get_stat"))
async def get_stat_handler(message: Message):
    await message.answer("Собираю данные и формирую CSV-файлы...")

    users = await db.get_all_users()
    posts = await db.get_all_posts()
    post_images = await db.get_all_post_images()
    module_questions = await db.get_all_module_questions()
    quizzes = await db.get_all_quizzes()

    files_to_send = []
    temp_files_paths = []

    try:
        if users:
            tmp_path, filename = await dicts_to_csv(users, 'users.csv')
            files_to_send.append(FSInputFile(tmp_path, filename=filename))
            temp_files_paths.append(tmp_path)

        if posts:
            tmp_path, filename = await dicts_to_csv(posts, 'posts.csv')
            files_to_send.append(FSInputFile(tmp_path, filename=filename))
            temp_files_paths.append(tmp_path)

        if post_images:
            tmp_path, filename = await dicts_to_csv(post_images, 'post_images.csv')
            files_to_send.append(FSInputFile(tmp_path, filename=filename))
            temp_files_paths.append(tmp_path)

        if module_questions:
            tmp_path, filename = await dicts_to_csv(module_questions, 'module_questions.csv')
            files_to_send.append(FSInputFile(tmp_path, filename=filename))
            temp_files_paths.append(tmp_path)

        if quizzes:
            tmp_path, filename = await dicts_to_csv(quizzes, 'quizzes.csv')
            files_to_send.append(FSInputFile(tmp_path, filename=filename))
            temp_files_paths.append(tmp_path)

        if not files_to_send:
            await message.answer("В базе нет данных для экспорта.")
            return

        await message.answer("Вот ваши данные:")
        for file in files_to_send:
            await message.answer_document(file)

    except Exception as e:
        await message.answer(f"Произошла ошибка при экспорте данных: {e}")
    finally:
        for path in temp_files_paths:
            if os.path.exists(path):
                os.remove(path)

