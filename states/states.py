from aiogram.dispatcher.filters.state import StatesGroup, State


class MakeOrderStates(StatesGroup):
    '''Класс для машины состояний'''

    need_milling = State()
    your_name = State()
    phone_number = State()
    need_shipping = State()
    set_shipping_address = State()
