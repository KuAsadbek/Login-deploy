from aiogram.fsm.state import StatesGroup,State

class StateUser(StatesGroup):
    school = State()
    name = State()
    city = State()
    number = State()
    py = State()
    py1 = State()
    check = State()
    comment = State()

    comment_uz = State()
    school_uz = State()
    name_uz = State()
    city_uz = State()
    number_uz = State()
    py_uz = State()
    py1_uz = State()
    check_uz = State()