from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .database.db import db


main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Модули', callback_data='modules_menu')],
    [InlineKeyboardButton(text='Письмо к себе', callback_data='review_menu')],
    [InlineKeyboardButton(text='Помощь', callback_data='help_menu')],
])

async def get_modules_keyboard(id):
    user = await db.get_user_by_id(id)
    if not user:
        return None
    modules_code = user['modules']

    module_names = [
        '1. ВУЗ VS Школа',
        '2. Поставить и достичь цель',
        '3. Управляй временем',
        '4. Контроль мотивации',
        '5. Без страха ошибок',
        '6. Работай в команде',
        '7. Расти через рефлексию',
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
        InlineKeyboardButton(text='Модули', callback_data='modules_menu'),
        InlineKeyboardButton(text='Далее', callback_data='next_theme')
    ]
])

module_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все модули курса', callback_data='modules_menu')],
    [InlineKeyboardButton(text='Следующий модуль!', callback_data='next_module')]
])


async def get_review_kb(id):
    user = await db.get_user_by_id(id)
    if not user:
        return None
    goals = user['goals']
    if not goals:
         kb = [
            [InlineKeyboardButton(text='Написать письмо себе', callback_data='add_goals')],
            [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
        ]
    else:
        kb = [
            [InlineKeyboardButton(text='Переписать письмо', callback_data='add_goals')],
            [InlineKeyboardButton(text='Посмотреть свое письмо', callback_data='view_goals')],
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
    options = [str(opt) for opt in options if (opt and opt != "nan")]

    buttons = [InlineKeyboardButton(text=opt, callback_data=f"quiz_answer:{opt}") for opt in options]

    inline_keyboard = [[button] for button in buttons]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

sync_data_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посты', callback_data='sync_posts'), InlineKeyboardButton(text='Картинки', callback_data='sync_images')],
    [InlineKeyboardButton(text='Вопросы', callback_data='sync_questions'), InlineKeyboardButton(text='Квизы', callback_data='sync_quizzes')],
    [InlineKeyboardButton(text='Все', callback_data='sync_all')], 
    [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
])

report_problem_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Технические вопросы', callback_data='report_technical_problem')],
    [InlineKeyboardButton(text='Проблема с работой бота', callback_data='report_bot_problem')],
    [InlineKeyboardButton(text='Проблема содержанием поста', callback_data='report_posts_problem')],
    [InlineKeyboardButton(text='Проблема с квизами', callback_data='report_quizzes_problem')],
    [InlineKeyboardButton(text='Проблема с вопросами', callback_data='report_questions_problem')],
    [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
])

back_to_report_problem_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='help_menu')]
])

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/update_data")],
        [KeyboardButton(text="/get_stat")],
        [KeyboardButton(text="/send_message_to_users")],
        [KeyboardButton(text="/send_letters")],
        [KeyboardButton(text="/start")],
    ],
    resize_keyboard=True
)

apply_sending_letters_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, отправить', callback_data='send_letters')],
    [InlineKeyboardButton(text='Нет, обратно в меню', callback_data='main_menu')]
])