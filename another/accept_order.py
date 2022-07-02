from another.request_to_API import get_user_basket
from settings.config import STORE_ADDRESS


async def check_and_accept_order(user_tlg_id, need_milling_data, client_name_data,
                           phone_number_data, need_shipping_data, user_address_data=None):
    '''Функция для формирования данных заказа в виде текста.'''

    response = await get_user_basket(user_tlg_id)

    # Нам придёт список списков
    # 'items_id',
    # 'items_id__items_name',
    # 'items_id__price',
    # 'items_number_in_basket',
    # 'items_id__number_of_items',

    text_for_message = f'<b><u>Давайте проверим заказ.</u></b>\n' \
                       f'<b>Помол:</b> {"нужен" if need_milling_data=="yes_mill" else "не нужен"}\n' \
                       f'<b>Доставка:</b> {user_address_data if need_shipping_data=="yes_ship" else "не требуется"}\n' \
                       f'<b>Имя:</b> {client_name_data}\n' \
                       f'<b>Телефон:</b> {phone_number_data}\n\n' \
                       f'<b>Состав заказа:</b>\n' \
                       f'<b>Наш адрес:</b> {STORE_ADDRESS}'
    total_price = 0
    for i_num, i_item in enumerate(response):
        item_name = i_item[1]
        items_number_in_basket = i_item[3]
        price = i_item[2] * items_number_in_basket
        total_price += price
        item_text = f'{i_num + 1}) {item_name} ({items_number_in_basket} шт.) {price} руб. '
        text_for_message = '\n'.join([text_for_message, item_text])

    total_price_text = f'\n<b><u>ИТОГО: {total_price}</u></b>'
    text_for_message = '\n'.join([text_for_message, total_price_text])
    return text_for_message


