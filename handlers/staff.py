from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import get_info_about_orders, post_req_for_add_order_to_archive, get_user_info
from keyboards.callback_data_bot import callback_for_stuff, callback_for_admins_orders_lst
from keyboards.inline_keyboard import stuff_formation_order_complete_inline
from settings.config import DP, BOT


async def press_button_complete_order(call: CallbackQuery, callback_data: dict):
    '''Обработчик для нажатия персоналом кнопки ЗАКАЗ ГОТОВ.'''

    await call.answer(text=f'{emojize(":robot:")} Сообщаю клиенту, переношу заказ в архив...')
    order_id = callback_data['order_id']
    chat_id = callback_data['chat_id']
    message_id = callback_data['message_id']

    # получаем заказ
    this_fu_order = await get_info_about_orders(order_id=order_id)
    # берём из него все данные
    order_data = {
        'order_id_before_receiving': order_id,
        'user': this_fu_order.get('user'),
        'pay_status': True,
        'execution_status': True,
        'order_items': this_fu_order.get('order_items'),
        'result_orders_price': this_fu_order.get('result_orders_price'),
        'need_milling': this_fu_order.get('need_milling'),
        'shipping': this_fu_order.get('shipping'),
        'shipping_address': this_fu_order.get('shipping_address'),
        'contact_telephone': this_fu_order.get('contact_telephone'),
    }

    # изменяем эти данные и посылаем их по другому адресу views
    response = await post_req_for_add_order_to_archive(order_data=order_data)
    if response == 400:
        await call.answer(text=f'{emojize(":robot:")}Запрос к серверу не удался. \nЗаказ не был удалён.', show_alert=True)
    else:
        # у персонала редактируется сообщение с заказом
        await BOT.edit_message_text(text=f'{emojize(":robot:")}Заказ № {order_id} выполнен✅', message_id=message_id, chat_id=chat_id)


async def orders_lst_for_admins(call: CallbackQuery):
    '''Обработчик для списка заказов, отдаваемого админам'''

    await call.answer(text='Список всех активных заказов, доступный админам бота. '
                           'Если бот ничего не ответил, значит заказы отсутствуют.'
                           'Отмечайте заказ, как выполненный, после передачи клиенту и получения оплаты.', show_alert=True)
    response = await get_info_about_orders()
    # Формируем текст для сообщения.
    for i_order in response:
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
        text_for_message = f'<b><ins>Номер заказа: <tg-spoiler> {i_order["id"]}' \
                           f'</tg-spoiler> </ins></b>\n<b>Cостав заказа:</b> \n'
        response_about_user = await get_user_info(user_id=i_order["user"])
        other_text = f'<b>\nИтоговая цена заказа:</b> <tg-spoiler>{result_orders_price}</tg-spoiler> руб.\n' \
                     f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                     f'<b>Статус выполнения:</b> {execution_status}\n' \
                     f'<b>Дата и время заказа:</b> {i_order["datetime"]}\n' \
                     f'<b>Помол</b>: {i_order["need_milling"]}\n' \
                     f'<b>Необходимость доставки:</b> {i_order["shipping"]}\n' \
                     f'<b>Адрес доставки:</b> {i_order["shipping_address"]}\n' \
                     f'<b>Контактный телефон:</b> {i_order["contact_telephone"]}\n' \
                     f'<b>Контактное лицо:</b> {response_about_user["user_name"]}'
        for i_item in order_items:
            text_for_message = ''.join([text_for_message, i_item, '\n'])
        text_for_message = ''.join([text_for_message, other_text])
        this_message = await call.message.answer(text=text_for_message)
        inline_keyboard = stuff_formation_order_complete_inline(order_id=i_order["id"], chat_id=call.from_user.id,
                                                                message_id=this_message.message_id)
        await this_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


def register_staff_handlers():
    '''Функция для регистрации обработчиков действий персонала.'''

    DP.register_callback_query_handler(press_button_complete_order, callback_for_stuff.filter(flag='order_complete'))
    DP.register_callback_query_handler(orders_lst_for_admins, callback_for_admins_orders_lst.filter(flag='orderslst'))
