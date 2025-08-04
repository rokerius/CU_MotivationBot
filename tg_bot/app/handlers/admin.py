import logging
import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
import gspread
from gspread_dataframe import get_as_dataframe 
import json

from ..database.db import db
from ..keyboards import main_menu_kb, sync_data_kb, admin_kb
from ..work_with_csv import dicts_to_csv
from ..utils import *

logger = logging.getLogger(__name__)

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
router = Router()

@router.message(Command("set_post"))
async def add_post_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    try:
        _, rest = message.text.split(' ', 1)
        module, theme, title, content = rest.split('|', 3)
        module, theme = int(module.strip()), int(theme.strip())
        title = title.strip()
        content = content.strip()
    except ValueError:
        await message.answer("Используйте формат: /set_post <номер модуля> | <номер темы> | <заголовок> | <содержимое>")
        return

    existing_post = await db.get_post_by_module_and_theme(module, theme)
    if existing_post:
        await message.answer("Пост с таким модулем и темой уже существовал, мы его заменили")
        await show_post_with_images(message, module, theme, db)
        await message.answer("Поста сверху больше не существует. Ниже - новый пост")

    post_id = await db.set_post(user_id=message.from_user.id, module=module,
                                theme=theme, title=title, content=content)

    logger.info(f"Setting post from user {message.from_user.id}: ({module}|{theme}|{title}|{content}) -> post id is {post_id}")

    post = await db.get_post_by_module_and_theme(module, theme)
    if post:
        await show_post_with_images(message, module, theme, db)
        await message.answer("К следующей теме?", reply_markup=main_menu_kb)



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
    logger.info(f"Setting image from user {message.from_user.id}: ({post['id']}|{image_url}")
    await message.answer("Картинка успешно добавлена к посту!")
    await message.answer('Главное меню', reply_markup=main_menu_kb)


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
    logger.info(f"Setting question from user {message.from_user.id}: ({module}|{question}")
    await message.answer("Вопрос к модулю успешно добавлен")
    await message.answer('Главное меню', reply_markup=main_menu_kb)


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
        logger.error(f"error during sending stats: {e}")
        await message.answer(f"Произошла ошибка при экспорте данных: {e}")
    finally:
        for path in temp_files_paths:
            if os.path.exists(path):
                os.remove(path)
    await message.answer('Главное меню', reply_markup=main_menu_kb)


@router.message(Command("update_data"))
async def update_data_from_google_sheet(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await message.answer("Получаю данные из гугл таблицы...")
    try:
        with open('credentials.json', 'r', encoding='utf-8') as f:
            credentials = json.load(f)
            print(credentials)
        gc = gspread.service_account_from_dict(credentials)
    except Exception as e:
        await message.answer(f'Не удалось подключиться к гугл api \n Ошибка: {e}')
        return
    
    try:
        posts_text = gc.open(GOOGLE_SHEET_NAME).get_worksheet(0)
        posts_images = gc.open(GOOGLE_SHEET_NAME).get_worksheet(1)
        questions = gc.open(GOOGLE_SHEET_NAME).get_worksheet(2)
        quizzes = gc.open(GOOGLE_SHEET_NAME).get_worksheet(3)
    except Exception as e:
        await message.answer(
            f'Ошибка при чтении таблиц. Возможно неправильное имя ({GOOGLE_SHEET_NAME}) или нет одной из страниц \n Ошибка: {e}')
        return
    await message.answer(
        f'Таблица {GOOGLE_SHEET_NAME} найдена. Выберите, что хотите синхронизировать:', 
        reply_markup=sync_data_kb)

    @router.callback_query(lambda c: c.data == 'sync_posts')
    async def sync_posts_callback(callback):
        await callback.message.answer('Синхронизируем посты...')
        df = get_as_dataframe(posts_text, evaluate_formulas=True).dropna(how='all')
        df['user_id'] = df['user_id'].fillna(1)
        logs = await db.update_posts_data(df)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer('Что-то еще?', reply_markup=sync_data_kb)

    @router.callback_query(lambda c: c.data == 'sync_images')
    async def sync_images_callback(callback):
        await callback.message.answer('Синхронизируем картинки...')
        df = get_as_dataframe(posts_images, evaluate_formulas=True).dropna(how='all')
        logs = await db.update_images_data(df)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer('Что-то еще?', reply_markup=sync_data_kb)


    @router.callback_query(lambda c: c.data == 'sync_questions')
    async def sync_questions_callback(callback):
        await callback.message.answer('Синхронизируем вопросы...')
        df = get_as_dataframe(questions, evaluate_formulas=True).dropna(how='all')
        logs = await db.update_questions_data(df)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer('Что-то еще?', reply_markup=sync_data_kb)


    @router.callback_query(lambda c: c.data == 'sync_quizzes')
    async def sync_quizzes_callback(callback):
        await callback.message.answer('Синхронизируем квизы...')
        df = get_as_dataframe(quizzes, evaluate_formulas=True).dropna(how='all')
        logs = await db.update_quizzes_data(df)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer('Что-то еще?', reply_markup=sync_data_kb)


    @router.callback_query(lambda c: c.data == 'sync_all')
    async def sync_all_callback(callback):
        df = get_as_dataframe(posts_text, evaluate_formulas=True).dropna(how='all')
        df_images = get_as_dataframe(posts_images, evaluate_formulas=True).dropna(how='all')
        df_quizzes = get_as_dataframe(quizzes, evaluate_formulas=True).dropna(how='all')
        df_questions = get_as_dataframe(questions, evaluate_formulas=True).dropna(how='all')
        df['user_id'] = df['user_id'].fillna(1)
        logs = await db.update_posts_data(df)
        logs.append('Переходим к синхронизации картинок...')
        await callback.message.answer('\n'.join(logs))
        logs = await db.update_images_data(df_images)
        logs.append('Переходим к синхронизации вопросов...')
        await callback.message.answer('\n'.join(logs))
        logs = await db.update_questions_data(df_questions)
        logs.append('Переходим к синхронизации квизов...')
        await callback.message.answer('\n'.join(logs))
        logs = await db.update_quizzes_data(df_quizzes)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer(f'Синхронизация завершена! \n Главное меню', reply_markup=main_menu_kb)

    @router.callback_query(lambda c: c.data == 'main_menu')
    async def main_menu_callback(callback):
        await callback.message.answer('Главное меню', reply_markup=main_menu_kb)


@router.message(Command("admin"))
async def admin_panel_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    
    await message.answer(
        "Админ-панель. Быстрый доступ к основным командам. \n\n Выберите команду",
        reply_markup=admin_kb
    )


@router.message(Command("call_database"))
async def call_database_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await message.answer("Введите команду для выполнения")

    @router.message(lambda m: m.text.startswith('SELECT'))
    async def call_database_callback(message):
        await message.answer(f"Выполняю запрос...")
        try:
            rows = await db.fetch(message.text)
            result = []
            for row in rows:
                result.append(f"{'\n'.join([f'{k}: {v}' for k, v in row.items()])}")
            for r in result:
                await message.answer(r)
        except Exception as e:
            await message.answer(f"Ошибка при выполнении запроса: {e}", reply_markup=admin_kb)


@router.message(Command("update_database"))
async def update_database_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await message.answer("Введите команду для выполнения")

    @router.message(lambda m: m.text.startswith('UPDATE') or m.text.startswith('DELETE') or m.text.startswith('INSERT'))
    async def update_database_callback(message):
        await message.answer(f"Выполняю запрос...")
        try:
            result = await db.execute(message.text)
            await message.answer(f"Запрос выполнен: {result}", reply_markup=admin_kb)
        except Exception as e:
            await message.answer(f"Ошибка при выполнении запроса: {e}", reply_markup=admin_kb)