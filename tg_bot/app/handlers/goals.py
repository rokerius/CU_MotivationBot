from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import os

from ..keyboards import *
from ..database.db import db
from .states import Review

bot = Bot(token=os.getenv('TOKEN')) # Иначе никак?
router = Router()


# Handler для начала ввода целей на семестр
@router.callback_query(lambda c: c.data == 'add_goals')
async def add_goals(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Review.add_goals)
    bot_message = await callback_query.message.edit_text('Введите цели на семестр', reply_markup=back_to_review_menu_kb)
    await state.update_data(bot_message_id=bot_message.message_id)

# Handler для сохранения целей на семестр
@router.message(Review.add_goals)
async def add_goals(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message_id = data.get('bot_message_id')
    await bot.delete_message(message.chat.id, bot_message_id)

    await state.clear()
    await db.add_goals(message.from_user.id, message.text)
    await message.delete()
    kb = await get_review_kb(message.from_user.id)
    await message.answer('Цели на семестр добавлены!', reply_markup=kb)

# Handler для просмотра целей пользователя
@router.callback_query(lambda c: c.data == 'view_goals')
async def view_goals(callback_query: CallbackQuery, state: FSMContext):
    user = await db.get_user_by_id(callback_query.from_user.id)
    goals = user['goals']
    await callback_query.message.edit_text(f'Твои цели на семестр: \n \n {goals}', reply_markup=back_to_review_menu_kb)
