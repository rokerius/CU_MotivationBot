from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from ..database.db import db
from ..keyboards import main_menu_kb

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    await message.answer('Привет!', reply_markup=main_menu_kb)

@router.message(Command('data'))
async def data(message: Message):
    await message.answer('Мы храним следующую информацию о тебе:\n')
    user = await db.get_user_by_id(message.from_user.id)
    if user:
        await message.answer(f"User found: {user}")
        answers = await db.get_answers(message.from_user.id)
        await message.answer(f"answers for user: {answers}")
    else:
        await message.answer("No data for user")
