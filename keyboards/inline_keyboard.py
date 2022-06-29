import random
import re
from aiogram.utils.emoji import emojize
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callback_data_bot import callback_for_next_or_prev_button, \
    callback_for_items_by_category, callback_for_category, \
    callback_for_add_item_to_basket, callback_back_to_categories, \
    callback_for_minus_plus_button, callback_for_orders_lst, callback_for_stuff, callback_for_milling, \
    callback_for_accept_order
from settings.config import KEYBOARD, RE_CATEGORY_LINK_PATTERN


def category_item_formation_keyboard(response_data, message_id):
    '''Формирователь инлайн клавиатуры для категорий товаров.'''

    inline_keyboard = InlineKeyboardMarkup(row_width=1)

    # формируем инлайн клавиатуру с категориями товаров
    results_in_page = response_data.get('results')
    emoj_lst = [
        # emojize(':pig:'), emojize(':pig_face:'), emojize(':pig_nose:'),
        # emojize(':cow:'), emojize(':cow_face:'), emojize(':ewe:'),
        # emojize(':ram:'), emojize(':deer:'), emojize(':chicken:'),
        emojize(':woman_cook:'),
        emojize(':cook:'),
        # emojize(':fork_and_knife_with_plate:'),
    ]
    for i_res_dct in results_in_page:
        category_id = i_res_dct['id']
        category_name = i_res_dct['category_name']
        inline_button = InlineKeyboardButton(
            text=' '.join([random.choice(emoj_lst), category_name]),
            callback_data=callback_for_category.new(
                category_id=category_id,
                message_id=message_id,
                flag='category_for_items'
            )
        )
        inline_keyboard.insert(inline_button)

    # формируем кнопки для навигации по страницам пагинации
    next_page_link = response_data.get('next')
    previous_page_link = response_data.get('previous')
    # создаём и добавляем кнопку при наличии ссылки
    if next_page_link:
        next_button_link = re.findall(RE_CATEGORY_LINK_PATTERN, next_page_link)[0]
        next_inline_button = InlineKeyboardButton(
            text=KEYBOARD['NEXT_STEP_CATEG'],
            callback_data=callback_for_next_or_prev_button.new(
                pagination_step=next_button_link,
                message_id=message_id,
                flag='pagination_categories',
            )
        )
        inline_keyboard.insert(next_inline_button)

    if previous_page_link:
        previous_button_link = re.findall(RE_CATEGORY_LINK_PATTERN, previous_page_link)
        if len(previous_button_link) == 0:
            previous_button_link = ''
        else:
            previous_button_link = previous_button_link[0]
        previous_inline_button = InlineKeyboardButton(
            text=KEYBOARD['BACK_STEP_CATEG'],
            callback_data=callback_for_next_or_prev_button.new(
                pagination_step=previous_button_link,
                message_id=message_id,
                flag='pagination_categories',
            )
        )
        inline_keyboard.insert(previous_inline_button)
    return inline_keyboard


def items_list_formation_keyboard(response_data, message_id=None):
    '''Функция для формирования инлайн клавиатуры со списком товаров'''

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    # формируем инлайн клавиатуру с товарами
    results_in_page = response_data.get('results')
    for i_item in results_in_page:
        # если товаров нет в наличии, то не выводим в общем списке
        if i_item['number_of_items'] < 1:
            continue
        item_name = i_item.get('items_name')
        price = i_item.get('price')

        # делаем кнопку для названия товара
        item_name_inline_button = InlineKeyboardButton(
            text=' '.join([emojize(':face_savoring_food:'), item_name]),
            callback_data=callback_for_items_by_category.new(
                item_id=i_item['id'],
                message_id=message_id,
                flag='item_detail'
            )
        )
        inline_keyboard.insert(item_name_inline_button)

        # делаем кнопку для цены товара
        item_price_inline_button = InlineKeyboardButton(
            text=' '.join([emojize(':credit_card:'), f'{price} руб.']),
            callback_data=callback_for_items_by_category.new(
                item_id=i_item['id'],
                message_id=message_id,
                flag='item_detail'
            )
        )
        inline_keyboard.insert(item_price_inline_button)

    # формируем кнопки для навигации по страницам пагинации
    next_page_link = response_data.get('next')
    previous_page_link = response_data.get('previous')
    # создаём и добавляем кнопку при наличии ссылки
    if next_page_link:
        next_button_link = re.findall(RE_CATEGORY_LINK_PATTERN, next_page_link)[0]
        next_inline_button = InlineKeyboardButton(
            text=KEYBOARD['NEXT_STEP_ITEM'],
            callback_data=callback_for_next_or_prev_button.new(
                pagination_step=next_button_link,
                message_id=message_id,
                flag='pagination_items'
            )
        )
        inline_keyboard.insert(next_inline_button)

    if previous_page_link:
        previous_button_link = re.findall(RE_CATEGORY_LINK_PATTERN, previous_page_link)
        if len(previous_button_link) == 0:
            previous_button_link = ''
        else:
            previous_button_link = previous_button_link[0]
        previous_inline_button = InlineKeyboardButton(
            text=KEYBOARD['BACK_STEP_ITEM'],
            callback_data=callback_for_next_or_prev_button.new(
                pagination_step=previous_button_link,
                message_id=message_id,
                flag='pagination_items'
            )
        )
        inline_keyboard.insert(previous_inline_button)

    category_items_button = InlineKeyboardButton(
        text=emojize(':BACK_arrow: Вернуться к категориям товаров'),
        callback_data=callback_back_to_categories.new(
            flag='back_to_categories',
            message_id=message_id
        )
    )
    inline_keyboard.insert(category_items_button)
    return inline_keyboard


def item_detail_formation_inline(category_id, item_id, message_id):
    '''Формирователь инлайн клавиатуры для детальной информации о товаре'''

    inline_keyboard = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KEYBOARD['BACK_STEP_ITEM'], callback_data=callback_for_category.new(
                    category_id=category_id,
                    message_id=message_id,
                    flag='category_for_items'
                )),
                InlineKeyboardButton(text=emojize('✅ Добавить в корзину'), callback_data=callback_for_add_item_to_basket.new(
                    item_id=item_id,
                    flag='add_item_to_basket_from_detail'
                ))
            ]
        ]
    )
    return inline_keyboard


def basket_formation_inline(message_id, user_tlg_id, item_id, items_numbers_in_basket, chat_id):
    '''Формирователь для клавиатуры в корзине товаров пользователя.'''

    # кнопки минус, плюс и количество товара в корзине
    minus_button = InlineKeyboardButton(
        text=KEYBOARD['MINUS_ITEM'],
        callback_data=callback_for_minus_plus_button.new(
            item_id=item_id,
            message_id=message_id,
            user_tlg_id=user_tlg_id,
            chat_id=chat_id,
            req_flag='minus',
            handler_flag='change_in_basket'
        )
    )
    plus_button = InlineKeyboardButton(
        text=KEYBOARD['PLUS_ITEM'],
        callback_data=callback_for_minus_plus_button.new(
            item_id=item_id,
            message_id=message_id,
            user_tlg_id=user_tlg_id,
            chat_id=chat_id,
            req_flag='plus',
            handler_flag='change_in_basket'
        )
    )

    number_items_button = InlineKeyboardButton(
        text=items_numbers_in_basket,
        callback_data=callback_for_minus_plus_button.new(
            item_id=item_id,
            message_id=message_id,
            user_tlg_id=user_tlg_id,
            chat_id=chat_id,
            req_flag='plus',
            handler_flag='change_in_basket'
        )
    )

    inline_keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
        [
            minus_button,
            number_items_button,
            plus_button
        ]
    ])

    return inline_keyboard


def order_formation_inline(order_id, chat_id, message_id):
    '''Формирователь инлайн клавиатуры для заказов. Кнопка отмены заказа.'''

    inline_keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=KEYBOARD['X_ORDER'],
                callback_data=callback_for_orders_lst.new(
                    flag='remove_order',
                    order_id=order_id,
                    chat_id=chat_id,
                    message_id=message_id,
                )
            ),
        ],
        [
            InlineKeyboardButton(
                text=KEYBOARD['PAY'],
                callback_data=callback_for_orders_lst.new(
                    flag='pay_order',
                    order_id=order_id,
                    chat_id=chat_id,
                    message_id=message_id,
                )
            ),
        ]
    ])
    return inline_keyboard


def stuff_formation_order_complete_inline(order_id, chat_id, message_id):
    '''Формирователь клавиатуры для персонала с кнопкой выполненного заказа.'''

    inline_keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=KEYBOARD['ORDER_COMPLETE'],
                callback_data=callback_for_stuff.new(
                    flag='order_complete',
                    order_id=order_id,
                    chat_id=chat_id,
                    message_id=message_id,
                )
            )
        ],
    ]
    )

    return inline_keyboard


def need_milling_formation_keyboard(message_id, answer_yes, answer_no, flag, user_tlg_id):
    '''Формирователь клавиатуры для шага 1 оформления заказа(помол).'''

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=KEYBOARD['YES'],
                callback_data=callback_for_milling.new(
                    answer=answer_yes,
                    message_id=message_id,
                    flag=flag,
                    user_tlg_id=user_tlg_id
                )
            ),
            InlineKeyboardButton(
                text=KEYBOARD['NO'],
                callback_data=callback_for_milling.new(
                    flag=flag,
                    message_id=message_id,
                    answer=answer_no,
                    user_tlg_id=user_tlg_id
                )
            ),
        ],
        [
            InlineKeyboardButton(
                text=KEYBOARD['CANCEL_MAKE_ORDER'],
                callback_data=callback_for_milling.new(
                    flag='cancel',
                    message_id=message_id,
                    answer='none',
                    user_tlg_id=user_tlg_id
                )
            ),
        ]
    ]
    )
    return inline_keyboard


def accept_order_inline_keyboard_formation(message_id, user_tlg_id):
    '''Формирователь клавиатуры для крайнего шага - подтверждения заказа.'''

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=KEYBOARD['YES'],
                callback_data=callback_for_accept_order.new(
                    flag='yes',
                    user_tlg_id=user_tlg_id,

                )
            ),
            InlineKeyboardButton(
                text=KEYBOARD['CANCEL_MAKE_ORDER'],
                callback_data=callback_for_milling.new(
                    flag='cancel',
                    message_id=message_id,
                    answer='none',
                    user_tlg_id=user_tlg_id
                )
            ),
        ],
    ]
    )
    return inline_keyboard


def formation_cancel_order_button(message_id, user_tlg_id):
    '''Формирование кнопки отмены заказа.'''

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=KEYBOARD['CANCEL_MAKE_ORDER'],
                callback_data=callback_for_milling.new(
                    flag='cancel',
                    message_id=message_id,
                    answer='none',
                    user_tlg_id=user_tlg_id
                )
            )
        ]
    ])
