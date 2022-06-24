from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ParseMode
from aiogram.utils.emoji import emojize
from aiogram import types

from another.request_to_API import get_info_about_orders, req_for_remove_order, get_user_basket, post_req_for_add_order, \
    clear_basket
from keyboards.callback_data_bot import callback_for_orders_lst
from keyboards.inline_keyboard import order_formation_inline
from keyboards.reply_keyboard import ORDER_KEYBRD
from settings.config import KEYBOARD, DP


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


async def add_order(message: types.Message):
    '''Обработчик для добавления нового заказа.'''

    user_tlg_id = message.from_user.id
    response_basket = await get_user_basket(user_tlg_id)
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

    order_data = {
        'user_tlg_id': user_tlg_id,
        'order_items': order_items,
        'result_orders_price': result_price,
    }
    response = await post_req_for_add_order(order_data)
    if response == 400:
        await message.answer(text=f'{emojize(":robot:")} Ошибка сервера. Заказ не был создан...')
    else:
        order_id = response['pk']

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

        await clear_basket(user_tlg_id)
        i_message = await message.answer(text=text_for_message, parse_mode=ParseMode.HTML)

        # формируем инлайн клавиатуру и обновляем сообщение, чтобы её добавить
        chat_id = i_message.chat.id
        message_id = message.message_id
        inline_keyboard = order_formation_inline(order_id, chat_id, message_id)
        await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


def register_orders_handlers():
    DP.register_message_handler(my_order, Text(equals=KEYBOARD['X_ORDER']))
    DP.register_callback_query_handler(remove_order, callback_for_orders_lst.filter(flag='remove_order'))
    DP.register_message_handler(add_order, Text(equals=KEYBOARD['MAKE_AN_ORDER']))
    DP.register_message_handler(my_order, Text(equals=KEYBOARD['MY_ORDER']))








