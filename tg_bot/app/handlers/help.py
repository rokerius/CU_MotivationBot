from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_album import AlbumMessage
import os
import logging
import asyncio

from ..keyboards import back_to_main_menu_kb
from .states import Help

logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TOKEN'))
router = Router()

first = True
@router.message(F.media_group_id)
async def report_problem(message: AlbumMessage, state: FSMContext):
    admin_ids = os.getenv('ADMIN_IDS').split()
    global first
    await asyncio.sleep(10)
    if first:
        for admin_id in admin_ids:
            await bot.send_message(admin_id, f'Пользователь @{message.from_user.username} сообщил о проблеме:')
            await message.copy_to(admin_id)
        await message.reply('Отказано.',  # пасхалка
                            reply_markup=back_to_main_menu_kb)
        first = False
    


@router.message(Help.report_problem, lambda message: message.media_group_id is None)
async def report_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message_id = data.get('bot_message_id')
    await bot.delete_message(message.chat.id, bot_message_id)
    await state.clear()

    await message.answer('Спасибо за ваше сообщение! Мы постараемся решить проблему как можно скорее.',
                        reply_markup=back_to_main_menu_kb)

    admin_ids = os.getenv('ADMIN_IDS').split()

    for admin_id in admin_ids:
        await bot.send_message(admin_id, f'Пользователь @{message.from_user.username} сообщил о проблеме:')
        await message.copy_to(admin_id)
    
    await message.delete()
    
