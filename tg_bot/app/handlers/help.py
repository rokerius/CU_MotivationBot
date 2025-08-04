from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from aiogram_album import AlbumMessage
import os
import logging
import asyncio

from ..keyboards import back_to_main_menu_kb
from .states import Help

logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TOKEN'))
router = Router()

first_photo = True
first = True
media = []
@router.message(lambda message: message.media_group_id is not None)
async def report_problem(message: AlbumMessage):
    admin_ids = os.getenv('ADMIN_IDS').split()
    global first
    global first_photo
    global media
    chat_id = message.chat.id
    if message.photo:
        if first_photo:
            first_photo = False
            media.append(InputMediaPhoto(media=message.photo[-1].file_id, caption=message.caption))
        else:
            media.append(InputMediaPhoto(media=message.photo[-1].file_id))

    if message.video:
        if first_photo:
            first_photo = False
            media.append(InputMediaVideo(media=message.video.file_id, caption=message.caption))
        else:
            media.append(InputMediaVideo(media=message.video.file_id))
    await asyncio.sleep(5)
    if first:
        first = False
        for admin_id in admin_ids:
            await bot.send_message(admin_id, f'Пользователь @{message.from_user.username} сообщил о проблеме:')
            await bot.send_media_group(admin_id, media=media)
        await bot.send_message(chat_id, f'Спасибо за сообщение! \nМы уже заметили эту проблему и работаем над её устранением. Скоро пофиксим❤',
                        reply_markup=back_to_main_menu_kb)
    else:
        await asyncio.sleep(10)
        first = True
        first_photo = True
        media = []


@router.message(lambda message: message.video_note or message.voice)
async def voice_or_video_note(message: Message):
    bot_message = await message.answer('Отказано.')
    await message.delete()
    await asyncio.sleep(2)
    await bot.delete_message(message.chat.id, bot_message.message_id)


@router.message(Help.report_problem, lambda message: message.media_group_id is None)
async def report_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message_id = data.get('bot_message_id')
    await bot.delete_message(message.chat.id, bot_message_id)
    await state.clear()

    await message.answer(f'Спасибо за сообщение! \nМы уже заметили эту проблему и работаем над её устранением. Скоро пофиксим❤',
                        reply_markup=back_to_main_menu_kb)

    admin_ids = os.getenv('ADMIN_IDS').split()

    for admin_id in admin_ids:
        await bot.send_message(admin_id, f'Пользователь @{message.from_user.username} сообщил о проблеме:')
        await message.copy_to(admin_id)
    
    await message.delete()
    
