from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup

from another.accept_order import check_and_accept_order
from another.request_to_API import get_user_basket
from keyboards.callback_data_bot import callback_for_milling
from keyboards.inline_keyboard import need_milling_formation_keyboard, accept_order_inline_keyboard_formation, \
    formation_cancel_order_button
from keyboards.reply_keyboard import MAIN_MENU
from settings.config import DP, KEYBOARD, ADMINS_ID_LST, ADMIN_PANEL, BOT
from states.states import MakeOrderStates


async def need_milling(message: types.Message):
    '''Первый шаг оформления заказа - спрашиваем о необходимости помола зерна.'''

    # Проверяем, что в корзине добавлены товары
    response_basket = await get_user_basket(user_tlg_id=message.from_user.id)
    if len(response_basket) == 0:
        await message.answer(text='Ваша корзина пуста...')
        return

    await message.answer(text='Оформляем Ваш заказ.', reply_markup=ReplyKeyboardRemove())
    await MakeOrderStates.need_milling.set()
    text_for_message = f'Нужен ли Вам помол?'
    answer_yes = 'yes_mill'
    answer_no = 'no_mill'
    inline_keyboard = need_milling_formation_keyboard(message.message_id, answer_yes, answer_no,
                                                      flag='mill', user_tlg_id=message.from_user.id)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def what_is_your_name(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Второй шаг - имя клиента.'''

    await call.answer(text='Следующий шаг оформления...')
    await state.update_data(need_milling=callback_data.get('answer'))
    await MakeOrderStates.your_name.set()
    text_for_message = f'Как к Вам можно обратиться?\n'
    inline_keyboard = formation_cancel_order_button(call.message.message_id, user_tlg_id=call.from_user.id)
    await call.message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


async def client_phone_number(message: types.Message, state: FSMContext):
    '''Третий шаг - номер телефона клиента.'''

    await state.update_data(client_name=message.text)
    await MakeOrderStates.phone_number.set()
    text_for_message = f'Введите номер телефона, чтобы мы могли с Вами связаться.\n'
    this_message = await message.answer(text=text_for_message)
    inline_keyboard = formation_cancel_order_button(this_message.message_id, user_tlg_id=message.from_user.id)
    await this_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


async def need_shipping(message: types.Message, state: FSMContext):
    '''Четвертый шаг - необходимость доставки.'''

    await state.update_data(phone_number=message.text)
    await MakeOrderStates.need_shipping.set()
    text_for_message = f'Оформить Вам доставку?\n' \
                       f'Это бесплатно при заказе от 1000 рублей.'
    answer_yes = 'yes_ship'
    answer_no = 'no_ship'
    inline_keyboard = need_milling_formation_keyboard(message.message_id, answer_yes, answer_no, flag='shipping',
                                                      user_tlg_id=message.from_user.id)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def shipping_address(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Пятый шаг - просим ввести адрес доставки'''

    need_shipping_flag = callback_data.get('answer')
    await state.update_data(need_shipping=need_shipping_flag)
    await MakeOrderStates.set_shipping_address.set()
    text_for_message = f'Введите адресс доставки'
    inline_keyboard = formation_cancel_order_button(call.message.message_id, user_tlg_id=call.from_user.id)
    await call.message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def accept_order_with_shipping(message: types.Message, state: FSMContext):
    '''Проверка и подтверждение заказа клиентом, когда доставка нужна.'''

    await state.update_data(user_address=message.text)
    state_data = await state.get_data()
    need_milling_data = state_data.get('need_milling')
    client_name_data = state_data.get('client_name')
    phone_number_data = state_data.get('phone_number')
    need_shipping_data = state_data.get('need_shipping')
    user_address_data = state_data.get('user_address')

    text_for_message = await check_and_accept_order(
        user_tlg_id=message.from_user.id,
        need_milling_data=need_milling_data,
        client_name_data=client_name_data,
        phone_number_data=phone_number_data,
        need_shipping_data=need_shipping_data,
        user_address_data=user_address_data
    )

    inline_keyboard = accept_order_inline_keyboard_formation(user_tlg_id=message.from_user.id,
                                                             message_id=message.message_id)
    await message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def accept_order_without_shipping(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Обработчик для подтверждения заказа, когда доставка не нужна.'''

    await call.answer(text='Адрес доставки не указан.')
    await state.update_data(user_address='Адрес доставки не указан.', need_shipping=callback_data.get('answer'))
    state_data = await state.get_data()
    need_milling_data = state_data.get('need_milling')
    client_name_data = state_data.get('client_name')
    phone_number_data = state_data.get('phone_number')
    need_shipping_data = state_data.get('need_shipping')
    user_address_data = state_data.get('user_address')

    text_for_message = await check_and_accept_order(
        user_tlg_id=callback_data.get('user_tlg_id'),
        need_milling_data=need_milling_data,
        client_name_data=client_name_data,
        phone_number_data=phone_number_data,
        need_shipping_data=need_shipping_data,
        user_address_data=user_address_data
    )

    inline_keyboard = accept_order_inline_keyboard_formation(user_tlg_id=call.from_user.id,
                                                             message_id=callback_data.get('message_id'))
    await call.message.answer(text=text_for_message, reply_markup=inline_keyboard)


async def cancel_male_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Обработчик для кнопки отмена оформления заказа.'''

    await call.answer(text='Вы отменили оформление заказа...(((', show_alert=True)
    await state.reset_state(with_data=True)
    await call.message.delete()

    await BOT.send_message(text=f'Вы перешли к главному меню', reply_markup=MAIN_MENU, chat_id=call.message.chat.id)
    if call.from_user.id in ADMINS_ID_LST:
        inline_keyboard = InlineKeyboardMarkup(
            row_width=1,
            inline_keyboard=[
                [
                    InlineKeyboardMarkup(text='Админ панель', url=ADMIN_PANEL),
                ]
            ],
        )
        await BOT.send_message(text=f'Админ панель', reply_markup=inline_keyboard, chat_id=call.message.chat.id)


def register_steps_for_make_order_handlers():
    '''Регистрация обработчиков для шагов оформления заказа.'''

    DP.register_message_handler(need_milling, Text(equals=KEYBOARD['MAKE_AN_ORDER']))
    DP.register_callback_query_handler(what_is_your_name, callback_for_milling.filter(flag='mill'),
                                       state=MakeOrderStates.need_milling)
    DP.register_callback_query_handler(shipping_address, callback_for_milling.filter(flag='shipping'))
    DP.register_message_handler(client_phone_number, state=MakeOrderStates.your_name)
    DP.register_message_handler(need_shipping, state=MakeOrderStates.phone_number)
    DP.register_callback_query_handler(
        shipping_address,
        callback_for_milling.filter(flag='shipping', answer='yes_ship'),
        state=MakeOrderStates.need_shipping
    )
    DP.register_message_handler(
        accept_order_with_shipping,
        state=MakeOrderStates.set_shipping_address
    )
    DP.register_callback_query_handler(
        accept_order_without_shipping,
        callback_for_milling.filter(flag='shipping', answer='no_ship'),
        state=MakeOrderStates.need_shipping
    )
    DP.register_callback_query_handler(cancel_male_order, callback_for_milling.filter(flag='cancel'), state='*')
