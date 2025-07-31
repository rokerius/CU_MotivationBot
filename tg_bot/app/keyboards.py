from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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

def create_quiz_options_kb(quiz: dict) -> InlineKeyboardMarkup:
    options = [
        quiz.get('option_1'),
        quiz.get('option_2'),
        quiz.get('option_3'),
        quiz.get('option_4'),
        quiz.get('option_5'),
    ]
    options = [opt for opt in options if opt]

    buttons = [InlineKeyboardButton(text=opt, callback_data=f"quiz_answer:{opt}") for opt in options]

    inline_keyboard = [[button] for button in buttons]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

sync_data_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посты', callback_data='sync_posts'), InlineKeyboardButton(text='Картинки', callback_data='sync_images')],
    [InlineKeyboardButton(text='Вопросы', callback_data='sync_questions'), InlineKeyboardButton(text='Квизы', callback_data='sync_quizzes')],
    [InlineKeyboardButton(text='Все', callback_data='sync_all')], 
    [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
])

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/set_post"), KeyboardButton(text="/set_image")],
        [KeyboardButton(text="/set_question"), KeyboardButton(text="/get_stat")],
        [KeyboardButton(text="/update_data"), KeyboardButton(text="/call_database")],
        [KeyboardButton(text="/update_database")],
        [KeyboardButton(text="Главное меню")],
    ],
    resize_keyboard=True
)