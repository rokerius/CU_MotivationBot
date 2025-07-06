from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .database.db import db


async def get_modules_keyboard(id):
    user = await db.get_user_by_id(id)
    if not user:
        return None
    modules_code = user['modules']

    module_names = [
        '1. Формат и роли',
        '2. Цели',
        '3. Тайм-менеджмент',
        '4. Мотивация',
        '5. Методы обучения',
        '6. Страх ошибок',
        '7. Команда',
        '8. Рефлексия'
    ]

    keyboard = []
    for i, name in enumerate(module_names):
        flag = ' ✅' if i < len(modules_code) and modules_code[i] == '1' else ''
        button = InlineKeyboardButton(text=name + flag, callback_data=f'module_{i + 1}')
        keyboard.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


theme_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Меню', callback_data='menu'),
        InlineKeyboardButton(text='Далее', callback_data='next_theme')
    ]
])

module_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Меню', callback_data='menu')],
    [InlineKeyboardButton(text='Следующий модуль!', callback_data='next_module')]
])

