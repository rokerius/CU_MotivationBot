from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import os
import logging

from ..keyboards import *
from ..database.db import db
from .states import Review

logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TOKEN'))
router = Router()


@router.callback_query(lambda c: c.data == 'add_goals')
async def add_goals(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Review.add_goals)
    bot_message = await callback_query.message.edit_text('Напиши письмо себе',
                                                         reply_markup=back_to_review_menu_kb)
    await state.update_data(bot_message_id=bot_message.message_id)


@router.message(Review.add_goals)
async def add_goals(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message_id = data.get('bot_message_id')
    await bot.delete_message(message.chat.id, bot_message_id)

    await state.clear()
    await db.add_goals(message.from_user.id, message.text)
    await message.delete()
    kb = await get_review_kb(message.from_user.id)
    logger.info(f"Setting goals for user {message.from_user.id}: {message.text}")
    await message.answer('Письмо отправлено!', reply_markup=kb)


@router.callback_query(lambda c: c.data == 'view_goals')
async def view_goals(callback_query: CallbackQuery, state: FSMContext):
    user = await db.get_user_by_id(callback_query.from_user.id)
    goals = user['goals']
    await callback_query.message.edit_text(f'Твое письмо: \n \n {goals}',
                                           reply_markup=back_to_review_menu_kb)
