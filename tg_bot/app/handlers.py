from aiogram.filters import Command
from aiogram.types import Message, Location, CallbackQuery
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from . import keyboards
from .database.db import db
from .utils import *

router = Router()
path = ""

class StateModule(StatesGroup):
    current_module = State()
    current_theme = State()



@router.message(Command('start'))
async def start(message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    kb = await keyboards.get_modules_keyboard(user.id)
    await message.answer('Привет! Я помогу тебе учиться и разбираться в нужных темах.'
                         'Выбери интересующую главу, и я пришлю подтемы для изучения.', reply_markup=kb)


@router.message(Command('data'))
async def data(message: Message):
    await message.answer('Мы храним следующую информацию о тебе:\n')
    user = await db.get_user_by_id(message.from_user.id)
    if user:
        await message.answer(f"User found: {user}")
    else:
        await message.answer("No data for user")



@router.callback_query(lambda c: c.data in ['module_' + str(i) for i in range(1, 9)])
async def process_time_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_module = int(callback_query.data.split('_')[-1])
    await state.update_data(current_module=selected_module)
    await state.update_data(current_theme=1)
    await callback_query.answer()
    await callback_query.message.answer(f'* описание {selected_module} модуля *')

    post = await db.get_post_by_module_and_theme(selected_module, 1)
    if post:
        await state.update_data(current_theme=1)
        await show_post_with_images(callback_query.message, selected_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=keyboards.theme)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! К следующему?',
                                            reply_markup=keyboards.module)
    await callback_query.message.delete()
    await callback_query.answer()


@router.callback_query(lambda c: c.data == 'next_theme')
async def next_theme_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_module = data.get('current_module')
    current_theme = data.get('current_theme', 1)

    next_theme = current_theme + 1

    post = await db.get_post_by_module_and_theme(current_module, next_theme)
    if post:
        await state.update_data(current_theme=next_theme)
        await show_post_with_images(callback_query.message, current_module, next_theme, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=keyboards.theme)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! К следующему?',
                                            reply_markup=keyboards.module)
    await callback_query.message.delete()
    await callback_query.answer()


@router.callback_query(lambda c: c.data == 'next_module')
async def next_theme_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_module = data.get('current_module')
    next_module = current_module + 1
    await callback_query.message.answer(f'* описание {next_module} модуля *')

    post = await db.get_post_by_module_and_theme(next_module, 1)
    if post:
        await state.update_data(current_theme=1)
        await state.update_data(current_module=next_module)
        await show_post_with_images(callback_query.message, next_module, 1, db)
        await callback_query.message.answer("К следующей теме?", reply_markup=keyboards.theme)
    else:
        await callback_query.message.answer('Это последняя тема в этом модуле! К следующему?',
                                            reply_markup=keyboards.module)
    await callback_query.message.delete()
    await callback_query.answer()



@router.callback_query(lambda c: c.data == 'menu')
async def menu(callback_query: CallbackQuery, state: FSMContext):
    user = callback_query.from_user
    kb = await keyboards.get_modules_keyboard(user.id)

    await callback_query.answer("Возвращаемся в главное меню!") # Можно оставить пустым или с сообщением

    await callback_query.message.answer(
        'Выберите интересующую главу, и я пришлю подтемы для изучения.', reply_markup=kb)

    await state.clear()


@router.message(Command("addpost"))
async def add_post_handler(message: Message):
    try:
        _, rest = message.text.split(' ', 1)
        module, theme, title, content = rest.split('|', 3)
        title = title.strip()
        content = content.strip()
    except ValueError:
        await message.answer("Используйте формат: /addpost Номер модуля | Номер темы | Заголовок | Содержимое")
        return

    post_id = await db.add_post(user_id=message.from_user.id, module=int(module), theme=int(theme), title=title, content=content)
    await message.answer(f"Пост добавлен с id = {post_id}")


@router.message(Command("addimage"))
async def add_image_handler(message: Message):
    _, rest = message.text.split(' ', 1)
    parts = rest.split('|', maxsplit=2)
    if len(parts) < 3:
        await message.answer("Используйте формат:\n/addimage номер_модуля | номер_темы | URL_картинки")
        return

    try:
        module = int(parts[0])
        theme = int(parts[1])
        image_url = parts[2].strip()
    except ValueError:
        await message.answer("Номера модуля и темы должны быть целыми числами.")
        return

    post = await db.get_post_by_module_and_theme(module, theme)
    if not post:
        await message.answer("Пост с таким модулем и темой не найден.")
        return

    await db.add_image_to_post(post_id=post['id'], image_url=image_url)
    await message.answer("Картинка успешно добавлена к посту.")



# # Инлайн с параметром
# @router.callback_query(lambda c: c.data in ['temperature', 'humidity', 'precipitation', 'wind_speed'])
# async def process_time_selection(callback_query: CallbackQuery, state: FSMContext):
#     selected_param = callback_query.data
#     await state.update_data(param=selected_param)
#     await callback_query.answer()
#     await state.set_state(Reg.choice)
#     await callback_query.message.answer(f'Выбери как будешь задавать точки:', reply_markup=keyboards.choice_inline)
#
#
# # Инлайн с типом ввода
# @router.callback_query(lambda c: c.data in ["Города", "Геометки", 'Координаты'])
# async def process_time_selection(callback_query: CallbackQuery, state: FSMContext):
#     selected_param = callback_query.data
#     await state.update_data(choice=selected_param)
#     await callback_query.answer()
#     if selected_param == "Города":
#         await state.set_state(Reg.city_1)
#         await callback_query.message.answer(f'Напиши первый город')
#
#     elif selected_param == "Геометки":
#         await state.set_state(Reg.geo_1)
#         await callback_query.message.answer(f'Скинь первую метку')
#
#     elif selected_param == "Координаты":
#         await state.set_state(Reg.point_1)
#         await callback_query.message.answer(f'Напиши координаты первой точки через пробел')
#
#
# # Считываем первые координаты
# @router.message(Reg.point_1)
# async def reg_point_1(message: Message, state: FSMContext):
#     try:
#         await state.update_data(point_1=message.text)
#         await state.set_state(Reg.final)
#         await message.answer(f'Напиши координаты второй точки через пробел')
#     except:
#         await message.answer('Проверь корректность введенной точки')
#         await state.set_state(Reg.point_1)
#
#
# # считываем первый город
# @router.message(Reg.city_1)
# async def reg_city_1(message: Message, state: FSMContext):
#     try:
#         await state.update_data(city_1=message.text)
#         await state.set_state(Reg.final)
#         await message.answer(f'Напиши второй город')
#     except:
#         await message.answer('Проверь корректность введенного города')
#         await state.set_state(Reg.city_1)
#
#
# # считываем первую геометку
# @router.message(Reg.geo_1)
# async def reg_geo_1(message: Location, state: FSMContext):
#     try:
#         await state.update_data(geo_1=str(message.location.longitude) + " " + str(message.location.latitude))
#         await state.set_state(Reg.final)
#         await message.answer(f'Скинь вторую геометку:')
#     except:
#         await message.answer("Что-то ты не то ввел, попробуй скинуть первую метку еще раз:")
#         await state.set_state(Reg.geo_1)
#
#
# # Получили все данные, выводим график
# @router.message(Reg.final)
# async def final(message: Location, state: FSMContext):
#     data = await state.get_data()
#     if data['choice'] == "Координаты":
#         await state.update_data(point_2=message.text)
#     if data['choice'] == "Города":
#         await state.update_data(city_2=message.text)
#     if data['choice'] == "Геометки":
#         try:
#             await state.update_data(geo_2=str(message.location.longitude) + " " + str(message.location.latitude))
#         except:
#             await message.answer("Что-то ты не то ввел, попробуй еще раз (выбери тип ввода точек)", reply_markup=keyboards.choice_inline)
#             await state.set_state(Reg.choice)
#             return 0
#     try:
#         data = await state.get_data()
#         await message.answer(f'Сейчас посмотрю, что можно найти, это может занять какое-то время...')
#
#         try:
#             error = ""
#             if data['choice'] == "Координаты":
#                 pass
#             if data['choice'] == "Города":
#                 pass
#             if data['choice'] == "Геометки":
#                 pass
#
#             if error == "":
#                 photo = FSInputFile(path)
#                 await message.answer_photo(photo)
#                 await message.answer(f'Ты можешь прямо сейчас выбрать по какому '
#                                  f'параметру перестроить график:', reply_markup=keyboards.param_after_final)
#             else:
#                 await message.answer(f'Произошла ошибка: ({error})\n\n Попробуйте еще раз: ', reply_markup=keyboards.choice_inline)
#         except:
#             await message.answer('Произошла ошибка, проблема на стороне API или некорректно введены точки')
#     except:
#         await message.answer("Что-то ты не то ввел, попробуй еще раз (выбери тип ввода точек):", reply_markup=keyboards.choice_inline)
#
#
# # После того, как график вывели, добавляем возможность редактировать
# @router.callback_query(lambda c: c.data in ['ftemperature', 'fhumidity', 'fprecipitation', 'fwind_speed'])
# async def param_after_final(callback_query: CallbackQuery, state: FSMContext):
#     selected_param = callback_query.data
#     await state.update_data(param=selected_param[1:])
#     await callback_query.answer()
#     await state.set_state(Reg.final)
#     try:
#         data = await state.get_data()
#         await callback_query.message.answer(f'Это может занять какое-то время...')
#         try:
#             error = ""
#             if data['choice'] == "Координаты":
#                 pass
#             if data['choice'] == "Города":
#                 pass
#             if data['choice'] == "Геометки":
#                 pass
#
#             if error == "":
#                 photo = FSInputFile(path)
#                 await callback_query.message.answer_photo(photo)
#                 await callback_query.message.answer(f'Ещё?', reply_markup=keyboards.param_after_final)
#             else:
#                 await callback_query.message.answer(error)
#
#         except:
#             await callback_query.message.answer('Произошла ошибка, проблема на стороне API или в обработке данных')
#     except:
#         await callback_query.message.answer("Что-то ты не то ввел, попробуй еще раз (выбери тип ввода точек)", reply_markup=keyboards.choice_inline)
#
#
# @router.callback_query(lambda c: c.data in ['end'])
# async def param_after_final(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.message.answer('Рад помочь)\n\nЕсли хотите начать заново, пишите /weather')
#     await callback_query.answer()
#     await state.clear()