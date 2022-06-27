from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from another.accept_order import check_and_accept_order
from keyboards.inline_keyboard import need_milling_formation_keyboard, accept_order_inline_keyboard_formation
from settings.config import DP, KEYBOARD
from states.states import MakeOrderStates


async def need_milling(message: types.Message):
    '''Первый шаг оформления заказа - спрашиваем о необходимости помола зерна.'''

    MakeOrderStates.need_milling.set()
    text_for_message = f'Нужен ли Вам помол?'
    answer_yes = 'yes_mill'
    answer_no = 'no_mill'
    inline_keyboard = need_milling_formation_keyboard(message.message_id, answer_yes, answer_no)
    await message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


async def what_is_your_name(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Второй шаг - имя клиента.'''

    await state.update_data(need_milling=callback_data.get('flag'))
    MakeOrderStates.your_name.set()
    text_for_message = f'Как к Вам можно обратиться?\n'
    await call.message.edit_text(text=text_for_message)


async def client_phone_number(message: types.Message, state: FSMContext):
    '''Третий шаг - номер телефона клиента.'''

    await state.update_data(client_name=message.text)
    MakeOrderStates.phone_number.set()
    text_for_message = f'Введи номер телефона, чтобы мы могли с Вами связаться.\n'
    await message.answer(text=text_for_message)


async def need_shipping(message: types.Message, state: FSMContext):
    '''Четвертый шаг - необходимость доставки.'''

    await state.update_data(phone_number=message.text)
    MakeOrderStates.need_shipping.set()
    text_for_message = f'Оформить Вам доставку?\n' \
                       f'Это бесплатно при заказе от 1000 рублей.'
    answer_yes = 'yes_ship'
    answer_no = 'no_ship'
    inline_keyboard = need_milling_formation_keyboard(message.message_id, answer_yes, answer_no)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def shipping_address(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Пятый шаг - где клиент получит товар, если выбрал доставку, то куда доставить товар.'''

    need_shipping_flag = callback_data.get('need_shipping')
    await state.update_data(need_shipping=need_shipping_flag)
    if need_shipping_flag == 'yes_ship':
        MakeOrderStates.set_shipping_address.set()
        text_for_message = f'Введите адресс доставки'
        await call.message.answer(text=text_for_message)
    else:
        pass


async def accept_order(message: types.Message, state: FSMContext):
    '''Проверка и подтверждение заказа клиентом.'''

    await state.update_data(users_address=message.text)
    state_data = await state.get_data()
    need_milling_data = state_data.get('need_milling')
    client_name_data = state_data.get('client_name')
    phone_number_data = state_data.get('phone_number')
    need_shipping_data = state_data.get('need_shipping')
    users_address_data = state_data.get('users_address')

    text_for_message = check_and_accept_order(
        user_tlg_id=message.from_user.id,
        need_milling_data=need_milling_data,
        client_name_data=client_name_data,
        phone_number_data=phone_number_data,
        need_shipping_data=need_shipping_data,
        users_address_data=users_address_data
    )
    inline_keyboard = accept_order_inline_keyboard_formation(message.message_id)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


def register_steps_for_make_order_handlers():
    '''Регистрация обработчиков для шагов оформления заказа.'''

    DP.register_message_handler(need_milling, Text(equals=KEYBOARD['MAKE_AN_ORDER']))
    DP.register_callback_query_handler()
    