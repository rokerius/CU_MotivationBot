from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from ..keyboards import main_menu_kb, back_to_main_menu_kb, get_modules_keyboard, get_review_kb

router = Router()

logger = logging.getLogger(__name__)

@router.callback_query(lambda c: c.data == 'main_menu')
async def main_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Главное меню', reply_markup=main_menu_kb)
    await state.clear()

@router.callback_query(lambda c: c.data == 'help_menu')
async def help_menu(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"User {callback_query.from_user.id} asking for help")
    await callback_query.message.edit_text('По техническим неполадкам пишите Денису: @rokerius',
                                           reply_markup=back_to_main_menu_kb)
    await state.clear()

@router.callback_query(lambda c: c.data == 'modules_menu')
async def modules_menu(callback_query: CallbackQuery):
    user = callback_query.from_user
    kb = await get_modules_keyboard(user.id)
    await callback_query.message.edit_text(
        'Выберите интересующий модуль или идите по порядку)', reply_markup=kb)


@router.callback_query(lambda c: c.data == 'review_menu')
async def review_menu(callback_query: CallbackQuery):
    kb = await get_review_kb(callback_query.from_user.id)
    await callback_query.message.edit_text('Ревью', reply_markup=kb)
