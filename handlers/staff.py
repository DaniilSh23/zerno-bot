from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import get_info_about_orders, post_req_for_add_order_to_archive
from keyboards.callback_data_bot import callback_for_stuff
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
        'user_tlg_id': this_fu_order.get('user_tlg_id'),
        'pay_status': this_fu_order.get('pay_status'),
        'execution_status': True,
        'order_items': this_fu_order.get('order_items'),
        'result_orders_price': this_fu_order.get('result_orders_price'),
    }
    # изменяем эти данные и посылаем их по другому адресу views
    response = await post_req_for_add_order_to_archive(order_data=order_data)
    if response == 400:
        await call.answer(text=f'{emojize(":robot:")}Запрос к серверу не удался. \nЗаказ не был удалён.', show_alert=True)
    else:
        # пользователю отправляется уведомление о выполнении заказа
        user_tlg_id = int(this_fu_order.get('user_tlg_id'))
        await BOT.send_message(chat_id=user_tlg_id, text=f'{emojize(":robot:")}Ваш заказ готов✅',)
        # у персонала редактируется сообщение с заказом
        await BOT.edit_message_text(text=f'{emojize(":robot:")}Заказ № {order_id} выполнен✅', message_id=message_id, chat_id=chat_id)


def register_staff_handlers():
    '''Функция для регистрации обработчиков действий персонала.'''

    DP.register_callback_query_handler(press_button_complete_order, callback_for_stuff.filter(flag='order_complete'))
