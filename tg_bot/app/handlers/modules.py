from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
import os
from ..keyboards import *
from ..database.db import db
from ..utils import *
from .states import StateModule

router = Router()

csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'descriptions.csv')
modules_description = read_modules_description_from_csv(csv_path)


@router.callback_query(lambda c: c.data in ['module_' + str(i) for i in range(1, 9)])
async def choosing_module(callback_query: CallbackQuery, state: FSMContext):
    selected_module = int(callback_query.data.split('_')[-1])
    await state.update_data(current_module=selected_module)
    await state.update_data(current_theme=1)
    await callback_query.message.answer(modules_description[selected_module])

    post = await db.get_post_by_module_and_theme(selected_module, 1)
    if post:
        await state.update_data(current_theme=1)
        await show_post_with_images(callback_query.message, selected_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! Пошли дальше?',
                                            reply_markup=module_kb)
    await safe_delete_message(callback_query.message)


@router.callback_query(lambda c: c.data == 'next_theme')
async def next_theme_handler(callback_query: CallbackQuery, state: FSMContext):
    gotten_data = await state.get_data()
    current_module = gotten_data.get('current_module')
    current_theme = gotten_data.get('current_theme', 1)

    next_theme = current_theme + 1

    post = await db.get_post_by_module_and_theme(current_module, next_theme)
    if post:
        await state.update_data(current_theme=next_theme)
        await show_post_with_images(callback_query.message, current_module, next_theme, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        quizzes = await db.get_quizzes_by_module(current_module)
        await state.update_data(quizzes=quizzes)
        all_done = True
        if quizzes:
            for i in range(len(quizzes)):
                await state.update_data(quiz_index=i)
                first_quiz = quizzes[i]
                first_quiz_done = await db.check_quizzes_done(callback_query.from_user.id, i, current_module)

                if not first_quiz_done:
                    all_done = False
                    kb = create_quiz_options_kb(first_quiz)
                    await callback_query.message.answer(first_quiz['question'], parse_mode="HTML", reply_markup=kb)
                    await state.set_state(StateModule.answering_quizzes)
                    break

        if not quizzes or all_done:
            question = await db.get_question_by_module(current_module)
            question_done = await db.check_questions_done(int(callback_query.from_user.id), current_module)
            if question and not question_done:
                await callback_query.message.answer(question, parse_mode="HTML")
                await state.set_state(StateModule.waiting_for_answer)
            elif question_done:
                await db.change_modules_done(callback_query.from_user.id, current_module, "1")
                await callback_query.message.answer(
                    "Ты уже отвечал на вопросы к этому модулю. Переходим к следующему модулю?",
                    reply_markup=module_kb
                )
                await state.set_state(StateModule.current_module)
                await state.update_data(current_theme=1)

            else:
                await db.change_modules_done(callback_query.from_user.id, current_module, "1")
                await callback_query.message.answer(
                    "Спасибо за ответы! Переходим к следующему модулю?",
                    reply_markup=module_kb
                )
                await state.set_state(StateModule.current_module)
                await state.update_data(current_theme=1)

    await safe_delete_message(callback_query.message)


@router.callback_query(lambda c: c.data == 'next_module')
async def next_module_handler(callback_query: CallbackQuery, state: FSMContext):
    gotten_data = await state.get_data()
    current_module = gotten_data.get('current_module')
    next_module = current_module + 1

    if next_module > max(modules_description.keys()):
        await safe_delete_message(callback_query.message)
        await end(callback_query, state)
        return

    await state.update_data(current_theme=1)
    await state.update_data(current_module=next_module)
    await callback_query.message.answer(modules_description[next_module], parse_mode="HTML")

    post = await db.get_post_by_module_and_theme(next_module, 1)
    if post:
        await show_post_with_images(callback_query.message, next_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! Пошли дальше?',
                                            reply_markup=module_kb)
    await safe_delete_message(callback_query.message)


@router.message(StateModule.waiting_for_answer)
async def handle_module_answer(message: Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    current_module = data.get('current_module')

    await db.save_answer(user_id=message.from_user.id, module=current_module, answer=user_answer)

    await message.answer("Спасибо за ответ! Переходим к следующему модулю?", reply_markup=module_kb)
    await db.change_modules_done(message.from_user.id, current_module, "1")
    await state.update_data(current_theme=1)
    await state.set_state(StateModule.current_module)


@router.message(StateModule.answering_quizzes)
async def handle_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    quizzes = data.get('quizzes', [])
    index = data.get('quiz_index', 0)
    current_quiz = quizzes[index]
    current_module = data.get('current_module')

    await db.save_quiz_answer(user_id=message.from_user.id,
                              module=current_module,
                              quiz=current_quiz.get('id'),
                              answer=message.text)

    index += 1
    if index < len(quizzes):
        next_quiz = quizzes[index]
        kb = create_quiz_options_kb(next_quiz)
        await message.answer(next_quiz['question'], parse_mode="HTML", reply_markup=kb)
        await state.update_data(quiz_index=index)

    else:
        await message.answer("Спасибо за ответы! Переходим к следующему?", reply_markup=module_kb)
        await state.set_state(StateModule.current_module)
        await state.update_data(current_theme=1)
        await state.update_data(quizzes=None, quiz_index=None)


@router.callback_query(lambda c: c.data and c.data.startswith('quiz_answer:'))
async def quiz_answer_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    user_answer = callback_query.data.split(':', 1)[1]
    data = await state.get_data()
    quizzes = data.get('quizzes', [])
    index = data.get('quiz_index', 0)
    current_quiz = quizzes[index]
    current_module = data.get('current_module')
    correct_answer = current_quiz.get('correct_answer')
    description = current_quiz.get('description')

    await db.save_quiz_answer(
        user_id=callback_query.from_user.id,
        module=current_module,
        quiz=current_quiz.get('id'),
        answer=user_answer
    )

    if user_answer == correct_answer:
        feedback = f"{current_quiz.get('question')}\n\n✅ Правильно! {correct_answer}\n\n{description}"
    else:
        feedback = f"{current_quiz.get('question')}\n\n❌ Неправильно. Правильный ответ: {correct_answer}\n\n{description}"

    await safe_delete_message(callback_query.message)

    # Отправляем фидбек
    feedback_msg = await callback_query.message.answer(feedback, parse_mode="HTML")

    # Отправляем сообщение с кнопкой "Далее"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Далее", callback_data="next_quiz")]
    ])
    await callback_query.message.answer("Нажми 'Далее', чтобы продолжить", reply_markup=kb)

    # Можно сохранить ID сообщения с фидбеком, если понадобится его удалить позже
    await state.update_data(last_feedback_message_id=feedback_msg.message_id)


@router.callback_query(lambda c: c.data == 'next_quiz')
async def next_quiz_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quizzes = data.get('quizzes', [])
    index = data.get('quiz_index', 0) + 1  # Переходим к следующему вопросу
    current_module = data.get('current_module')

    # Удаляем сообщение с кнопкой "Далее" чтобы очистить чат
    try:
        await callback_query.message.delete()
    except Exception:
        pass

    # Если нужно, можно удалить сообщение с прошлым фидбеком тоже:
    last_feedback_message_id = data.get('last_feedback_message_id')
    if last_feedback_message_id:
        try:
            await callback_query.message.chat.delete_message(last_feedback_message_id)
        except Exception:
            pass

    if index < len(quizzes):
        next_quiz = quizzes[index]
        kb = create_quiz_options_kb(next_quiz)
        await callback_query.message.answer(next_quiz['question'], parse_mode="HTML", reply_markup=kb)
        await state.update_data(quiz_index=index)
    else:
        question = await db.get_question_by_module(current_module)
        question_done = await db.check_questions_done(callback_query.from_user.id, current_module)
        if question and not question_done:
            await callback_query.message.answer(question, parse_mode="HTML")
            await state.set_state(StateModule.waiting_for_answer)
        elif question_done:
            await callback_query.message.answer(
                "Ты уже отвечал на вопросы к этому модулю. Переходим к следующему?",
                reply_markup=module_kb
            )
            await state.set_state(StateModule.current_module)
            await state.update_data(current_theme=1)
        else:
            await callback_query.message.answer(
                "Спасибо за ответы! Переходим к следующему модулю?",
                reply_markup=module_kb
            )
            await state.set_state(StateModule.current_module)
            await state.update_data(current_theme=1)

        await db.change_modules_done(callback_query.from_user.id, current_module, "1")
        await state.update_data(quizzes=None, quiz_index=None)

    await safe_delete_message(callback_query.message)


async def end(callback_query: CallbackQuery, state: FSMContext):
    answers = await db.get_answers(callback_query.from_user.id)
    await callback_query.message.answer('Это был последний модуль! Спасибо за прохождение!\n\n'
                                        'Вот ответы, которые ты давал на наши вопросы:')
    questions = answers["questions"]
    message_text = ""
    for q in questions:
        title = await db.get_question_by_module(int(q['module']))
        message_text += f"❓ <b>{title[:30].strip()}...</b>\n"
        message_text += f"💡 {q['answer']}\n\n"
    await callback_query.message.answer(
        message_text.strip(),
        parse_mode="HTML"
    )
    await state.clear()

    kb = await get_review_kb(callback_query.from_user.id)
    await callback_query.message.answer('Напиши себе будущему. Это может быть всё, что угодно: напутствие, слова поддержки, напоминание, шутка или мотивирующая цитата. Через полтора месяца бот отправит тебе сообщение', reply_markup=kb)
