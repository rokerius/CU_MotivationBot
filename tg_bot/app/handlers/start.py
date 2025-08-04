from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import logging

from ..database.db import db
from ..keyboards import main_menu_kb, back_to_main_menu_kb
from ..utils import is_admin

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('start'))
async def start(message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username)
    logger.info(f"New user: ({user.id}, {user.username}, {user.first_name} {user.last_name})")
    await message.answer('Привет!', reply_markup=main_menu_kb)

@router.message(Command('help'))
async def help(message: Message):
    logger.info(f"User {message.from_user.id} asking for help")
    await message.message.edit_text('По техническим вопросам пишите Денису: @rokerius',
                                           reply_markup=back_to_main_menu_kb)

@router.message(Command('reset_my_data'))
async def reset(message: Message):
    logger.info(f"User {message.from_user.id} reset his data")
    user = message.from_user
    async with db.pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE id = $1", user.id)
    await message.answer('Данные о текущем пользователе удалены')
    await db.add_user(user.id, user.username)
