from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import asyncio

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
    await callback_query.answer()
    await callback_query.message.delete()

# Handler для перехода к следующей теме внутри модуля
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
        if quizzes:
            await state.update_data(quizzes=quizzes, quiz_index=0)
            first_quiz = quizzes[0]
            kb = create_quiz_options_kb(first_quiz)
            await callback_query.message.answer(first_quiz['question'], reply_markup=kb)
            await state.set_state(StateModule.answering_quizzes)
        else:
            question = await db.get_question_by_module(current_module)
            if question:
                await callback_query.message.answer(question)
                await state.set_state(StateModule.waiting_for_answer)
            else:
                await db.change_modules_done(callback_query.from_user.id, current_module, "1")
                await callback_query.message.answer(
                    "Спасибо за ответы! Переходим к следующему модулю?",
                    reply_markup=module_kb
                )
                await state.set_state(StateModule.current_module)
                await state.update_data(current_theme=1)
                await callback_query.message.answer('Перейдем дальше?', reply_markup=module_kb)

    await callback_query.message.delete()


@router.callback_query(lambda c: c.data == 'next_module')
async def next_module_handler(callback_query: CallbackQuery, state: FSMContext):
    gotten_data = await state.get_data()
    current_module = gotten_data.get('current_module')
    next_module = current_module + 1

    if next_module > max(modules_description.keys()):
        await callback_query.message.delete()
        await callback_query.answer()
        await end(callback_query, state)
        return

    await state.update_data(current_theme=1)
    await state.update_data(current_module=next_module)
    await callback_query.message.answer(modules_description[next_module])

    post = await db.get_post_by_module_and_theme(next_module, 1)
    if post:
        await show_post_with_images(callback_query.message, next_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=theme_kb)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! Пошли дальше?',
                                            reply_markup=module_kb)
    await callback_query.message.delete()


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
        await message.answer(next_quiz['question'], reply_markup=kb)
        await state.update_data(quiz_index=index)

    else:
        await message.answer("Спасибо за ответы! Переходим к следующему модулю?", reply_markup=module_kb)
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

    await db.save_quiz_answer(
        user_id=callback_query.from_user.id,
        module=current_module,
        quiz=current_quiz.get('id'),
        answer=user_answer
    )

    if user_answer == correct_answer:
        feedback = f"✅ Правильно! {correct_answer}"
    else:
        feedback = f"❌ Неправильно. Правильный ответ: {correct_answer}"

    await callback_query.answer()
    await callback_query.message.delete()

    feedback_msg = await callback_query.message.answer(feedback)

    await asyncio.sleep(2)
    await feedback_msg.delete()

    index += 1
    if index < len(quizzes):
        next_quiz = quizzes[index]
        kb = create_quiz_options_kb(next_quiz)
        await callback_query.message.answer(next_quiz['question'], reply_markup=kb)
        await state.update_data(quiz_index=index)
    else:
        question = await db.get_question_by_module(current_module)
        if question:
            await callback_query.message.answer(question)
            await state.set_state(StateModule.waiting_for_answer)
        else:
            await callback_query.message.answer(
                "Спасибо за ответы! Переходим к следующему модулю?",
                reply_markup=module_kb
            )
            await state.set_state(StateModule.current_module)
            await state.update_data(current_theme=1)

        await db.change_modules_done(callback_query.from_user.id, current_module, "1")
        await state.update_data(quizzes=None, quiz_index=None)


async def end(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Конец')
    await state.clear()
