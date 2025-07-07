from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .database.db import db


main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Модули', callback_data='modules_menu')],
    [InlineKeyboardButton(text='Ревью', callback_data='review_menu')],
    [InlineKeyboardButton(text='Помощь', callback_data='help_menu')],
])

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
    keyboard.append([InlineKeyboardButton(text='Главное меню', callback_data='main_menu')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


theme_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Меню', callback_data='modules_menu'),
        InlineKeyboardButton(text='Далее', callback_data='next_theme')
    ]
])

module_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Меню', callback_data='modules_menu')],
    [InlineKeyboardButton(text='Следующий модуль!', callback_data='next_module')]
])


async def get_review_kb(id):
    user = await db.get_user_by_id(id)
    if not user:
        return None
    goals = user['goals']
    if not goals:
         kb = [
            [InlineKeyboardButton(text='Добавить цели на семестр', callback_data='add_goals')],
            [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
        ]
    else:
        kb = [
            [InlineKeyboardButton(text='Изменить цели на семестр', callback_data='add_goals')],
            [InlineKeyboardButton(text='Посмотреть свои цели', callback_data='view_goals')],
            [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

back_to_review_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='review_menu')]
])

back_to_main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
])