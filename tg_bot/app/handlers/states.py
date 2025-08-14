from aiogram.fsm.state import StatesGroup, State

class StateModule(StatesGroup):
    current_module = State()
    current_theme = State()
    waiting_for_answer = State()
    answering_quizzes = State()

class Letter(StatesGroup):
    add_letter = State()

class Help(StatesGroup):
    report_problem = State()

class AdminStates(StatesGroup):
    send_message_to_users = State()
    update_database = State()
    call_database = State()
    send_letters = State()
