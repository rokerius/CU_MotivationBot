from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import os
import logging

from ..keyboards import back_to_main_menu_kb
from .states import Help

logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TOKEN'))
router = Router()


@router.message(Help.report_problem)
async def report_problem(message: Message, state: FSMContext):
    logger.warning(f'{message.from_user.username} сообщил о проблеме: {message.text}')

    data = await state.get_data()
    bot_message_id = data.get('bot_message_id')
    await bot.delete_message(message.chat.id, bot_message_id)

    caption = f'@{message.from_user.username} сообщил о проблеме:\n{message.text}'
    admin_ids = os.getenv('ADMIN_IDS').split()

    for admin_id in admin_ids:
        await bot.send_message(admin_id, caption)
    await message.answer('Спасибо за ваше сообщение! Мы постараемся решить проблему как можно скорее.',
                        reply_markup=back_to_main_menu_kb)
    await message.delete()
    await state.clear()
