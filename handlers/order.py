from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ParseMode
from aiogram.utils.emoji import emojize
from aiogram import types

from another.request_to_API import get_info_about_orders, req_for_remove_order, get_user_basket, post_req_for_add_order, \
    clear_basket, post_req_for_add_new_user
from keyboards.callback_data_bot import callback_for_orders_lst, callback_for_accept_order
from keyboards.inline_keyboard import order_formation_inline, stuff_formation_order_complete_inline
from keyboards.reply_keyboard import ORDER_KEYBRD
from settings.config import KEYBOARD, DP, BOT, STAFF_ID


async def my_order(message: types.Message):
    '''Обработчик для нажатия кнопки МОЙ ЗАКАЗ.'''

    await message.answer(text=f'{emojize(":robot:")} Раздел ЗАКАЗЫ {emojize(":spiral_notepad:")}', reply_markup=ORDER_KEYBRD)
    user_tlg_id = message.from_user.id
    response = await get_info_about_orders(user_tlg_id)
    if response == 400:
        await message.answer(text=f'{emojize(":robot:")} Не удалось выполнить запрос к серверу...')
    else:
        for i_order in response:
            order_id = i_order.get('pk')
            if i_order.get('pay_status'):
                pay_status = 'Оплачен'
            else:
                pay_status = 'НЕ оплачен'
            if i_order.get('execution_status'):
                execution_status = 'Готов'
            else:
                execution_status = 'НЕ готов'
            order_items = i_order.get('order_items').split('\n')
            result_orders_price = i_order.get('result_orders_price')
            text_for_message = f'<b><ins>Номер заказа: <tg-spoiler> {order_id}' \
                               f'</tg-spoiler> </ins></b>\n<b>Cостав заказа:</b> \n'
            other_text = f'<b>\nИтоговая цена заказа:</b> <tg-spoiler>{result_orders_price}</tg-spoiler> руб.\n' \
                                 f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                                 f'<b>Статус выполнения:</b> {execution_status}'
            for i_item in order_items:
                text_for_message = ''.join([text_for_message, i_item, '\n'])
            text_for_message = ''.join([text_for_message, other_text])
            i_message = await message.answer(text=text_for_message)
            chat_id = i_message.chat.id
            message_id = message.message_id
            inline_keyboard = order_formation_inline(order_id, chat_id, message_id)
            await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


async def remove_order(call: CallbackQuery, callback_data: dict):
    '''Обработчик для удаления заказа из БД.'''

    await call.answer(text=f'{emojize(":robot:")} Выполняю запрос к серверу для удаления заказа...')
    order_id = callback_data['order_id']
    # chat_id = callback_data['chat_id']
    # message_id = callback_data['message_id']
    response = await req_for_remove_order(order_id=order_id)
    if response == 200:
        await call.message.delete()
    elif response == 400:
        await call.answer(text=f'{emojize(":robot:")}Запрос к серверу не удался. \nЗаказ не был удалён.', show_alert=True)


async def add_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    '''Обработчик для добавления нового заказа.'''

    user = callback_data.get('user_tlg_id')
    user_tlg_name = call.from_user.username
    state_data = await state.get_data()
    need_milling_data = state_data.get('need_milling')
    client_name_data = state_data.get('client_name')
    phone_number_data = state_data.get('phone_number')
    need_shipping_data = state_data.get('need_shipping')
    user_address_data = state_data.get('user_address')
    print(f'{need_shipping_data, need_milling_data, client_name_data}')

    response_basket = await get_user_basket(user_tlg_id=user)
    order_items = ''
    result_price = 0
    for i_item in response_basket:
        items_name = i_item[1]
        price = i_item[2]
        items_number_in_basket = i_item[3]

        result_price += price
        order_items = ''.join([
            order_items,
            f'Название товара: {items_name}\n',
            f'Количество: {items_number_in_basket} шт.\n',
            f'Цена за шт.: {price} руб.\n**********\n',
        ])

    # Формируем данные для запроса к модели пользователя.
    user_data = {
        'user_tlg_id': user,
        'user_tlg_name': user_tlg_name if user_tlg_name else None,
        'user_name': client_name_data,
        'last_shipping_address': user_address_data
    }
    response_user = await post_req_for_add_new_user(user_data=user_data)
    if not response_user:
        return await call.message.answer(text=f'{emojize(":robot:")} Ошибка сервера. Заказ не был создан...')

    # Формируем данные POST запроса для создания нового заказа.
    order_data = {
        'user': user,
        'order_items': order_items,
        'result_orders_price': result_price,
        # 'pay_status': False,
        # 'execution_status': False,
        'need_milling': True if need_milling_data == 'yes_milling' else False,
        'shipping': True if need_shipping_data == 'yes_ship' else False,
        'shipping_address': user_address_data,
        'contact_telephone': phone_number_data
    }
    response = await post_req_for_add_order(order_data)
    if response == 400:
        await call.message.answer(text=f'{emojize(":robot:")} Ошибка сервера. Заказ не был создан...')
    else:
        order_id = response['id']

        # формируем текст для сообщения
        if response.get('pay_status'):
            pay_status = 'Оплачен'
        else:
            pay_status = 'НЕ оплачен'
        if response.get('execution_status'):
            execution_status = 'Готов'
        else:
            execution_status = 'НЕ готов'
        order_items = response.get('order_items').split('\n')
        result_orders_price = response.get('result_orders_price')
        text_for_message = f'<b><ins>Номер заказа: <tg-spoiler> {order_id}' \
                           f'</tg-spoiler> </ins></b>\n<b>Cостав заказа:</b> \n'
        other_text = f'<b>\nИтоговая цена заказа:</b> <tg-spoiler>{result_orders_price}</tg-spoiler> руб.\n' \
                     f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                     f'<b>Статус выполнения:</b> {execution_status}'
        for i_item in order_items:
            text_for_message = ''.join([text_for_message, i_item, '\n'])
        text_for_message = ''.join([text_for_message, other_text])

        await clear_basket(user)
        i_message = await call.message.answer(text=text_for_message, parse_mode=ParseMode.HTML)

        # формируем инлайн клавиатуру и обновляем сообщение, чтобы её добавить
        chat_id = i_message.chat.id
        message_id = i_message.message_id
        inline_keyboard = order_formation_inline(order_id, chat_id, message_id)
        await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)

        # Сбрасываем машину состояний для пользователя
        await state.reset_state(with_data=True)

        # Отправляем заказ персоналу
        for i_member in STAFF_ID:
            inline_keyboard = stuff_formation_order_complete_inline(order_id=order_id,
                                                                    chat_id=i_member, message_id=message_id)
            await BOT.send_message(chat_id=i_member, text=text_for_message, reply_markup=inline_keyboard)


def register_orders_handlers():
    DP.register_message_handler(my_order, Text(equals=KEYBOARD['X_ORDER']))
    DP.register_callback_query_handler(remove_order, callback_for_orders_lst.filter(flag='remove_order'))
    DP.register_callback_query_handler(add_order, callback_for_accept_order.filter(flag='yes'), state='*')
    DP.register_message_handler(my_order, Text(equals=KEYBOARD['MY_ORDER']))






