from aiogram.fsm.state import StatesGroup, State

class StateModule(StatesGroup):
    current_module = State()
    current_theme = State()
    waiting_for_answer = State()
    answering_quizzes = State()

class Review(StatesGroup):
    add_goals = State()
