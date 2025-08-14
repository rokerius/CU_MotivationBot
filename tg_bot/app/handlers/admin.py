import logging
import os
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
import gspread
from gspread_dataframe import get_as_dataframe 
import json

from ..database.db import db
from ..keyboards import main_menu_kb, sync_data_kb, admin_kb, apply_sending_letters_kb
from ..utils import *
from .states import AdminStates

logger = logging.getLogger(__name__)

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
router = Router()
bot = Bot(token=os.getenv('TOKEN'))


@router.message(Command("get_stat"))
async def get_stat_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
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
        df_posts = get_as_dataframe(posts_text, evaluate_formulas=True).dropna(how='all')
        df_images = get_as_dataframe(posts_images, evaluate_formulas=True).dropna(how='all')
        df_quizzes = get_as_dataframe(quizzes, evaluate_formulas=True).dropna(how='all')
        df_questions = get_as_dataframe(questions, evaluate_formulas=True).dropna(how='all')
        df_posts['user_id'] = df_posts['user_id'].fillna(1)
        logs = await db.update_all_data(df_posts, df_images, df_questions, df_quizzes)
        await callback.message.answer('\n'.join(logs))
        await callback.message.answer(f'Синхронизация завершена!', reply_markup=main_menu_kb)


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
async def call_database_handler(message: Message, state):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await state.set_state(AdminStates.call_database)
    await message.answer("Введите команду для выполнения")

    @router.message(AdminStates.call_database)
    async def call_database_callback(message, state):
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
        await state.clear()


@router.message(Command("update_database"))
async def update_database_handler(message: Message, state):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await state.set_state(AdminStates.update_database)
    await message.answer("Введите команду для выполнения")

    @router.message(AdminStates.update_database)
    async def update_database_callback(message, state):
        await message.answer(f"Выполняю запрос...")
        try:
            result = await db.execute(message.text)
            await message.answer(f"Запрос выполнен: {result}", reply_markup=admin_kb)
        except Exception as e:
            await message.answer(f"Ошибка при выполнении запроса: {e}", reply_markup=admin_kb)
        await state.clear()


@router.message(Command("send_message_to_users"))
async def send_message_to_users_handler(message: Message, state):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await state.set_state(AdminStates.send_message_to_users)
    await message.answer("Введите сообщение для отправки пользователям")

    @router.message(AdminStates.send_message_to_users)
    async def send_message_to_users_callback(message, state):
        if not is_admin(message.from_user.username):
            await message.answer("Недостаточно прав 🤬")
            return
        await message.answer(f"Выполняю запрос...")
        try:
            users = await db.get_all_users()
            for user in users:
                await bot.send_message(user['id'], message.text)
        except Exception as e:
            await message.answer(f"Ошибка при отправке сообщения: {e}", reply_markup=admin_kb)
        await state.clear()
        await message.answer('Сообщение отправлено!', reply_markup=main_menu_kb)


@router.message(Command("send_letters"))
async def send_letters_handler(message: Message):
    if not is_admin(message.from_user.username):
        await message.answer("Недостаточно прав 🤬")
        return
    await message.answer("Точно хотите отправить письма всем пользователям?", reply_markup=apply_sending_letters_kb)

    @router.callback_query(lambda c: c.data == 'send_letters')
    async def send_letters_callback(callback, state):
        await callback.message.answer("Введите текст перед письмом")
        await state.set_state(AdminStates.send_letters)

        @router.message(AdminStates.send_letters)
        async def send_letters_callback(message, state):
            users = await db.get_all_users()
            try:
                for user in users:
                    if not user['letter']:
                        continue
                    text = f"{message.text}\n\n{user['letter']}"
                    await bot.send_message(user['id'], text)
            except Exception as e:
                await callback.message.answer(f"Ошибка при отправке писем: {e}")
            await callback.message.answer('Письма отправлены!', reply_markup=main_menu_kb)
            await state.clear()