from another.request_to_API import get_user_basket


def check_and_accept_order(user_tlg_id, need_milling_data, client_name_data,
                           phone_number_data, need_shipping_data,users_address_data=None):
    '''Функция для формирования данных заказа в виде текста.'''

    items_in_basket = await get_user_basket(user_tlg_id)

    # Нам придёт список списков
    # 'items_id',
    # 'items_id__items_name',
    # 'items_id__price',
    # 'items_number_in_basket',
    # 'items_id__number_of_items',

    text_for_message = f'<b>Помол:</b> {"нужен" if need_milling_data=="yes_mill" else "не нужен"}\n' \
                       f'<b>Доставка:</b> {users_address_data if need_shipping_data=="yes_ship" else "не требуется"}\n' \
                       f'<b>Имя:</b> {client_name_data}\n' \
                       f'<b>Телефон:</b> {phone_number_data}\n\n' \
                       f'<b>Состав заказа:</b>\n'

    for i_num, i_item in enumerate(items_in_basket):
        item_name = i_item[1]
        items_number_in_basket = i_item[3]
        price = i_item[2] * items_number_in_basket

        item_text = f'{i_num}) {item_name} ({items_number_in_basket} шт.) {price} руб. '
        text_for_message = '\n'.join([text_for_message, item_text])

    return text_for_message


