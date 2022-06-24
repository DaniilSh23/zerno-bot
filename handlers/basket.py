import random

from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize
from aiogram import types

from another.request_to_API import add_item_in_basket, get_user_basket, \
    remove_item_from_basket, clear_basket
from keyboards.callback_data_bot import callback_for_add_item_to_basket, callback_for_minus_plus_button
from keyboards.inline_keyboard import basket_formation_inline
from keyboards.reply_keyboard import BASKET_KEYBRD
from settings.config import KEYBOARD, DP, BOT


async def add_item_to_basket(call: CallbackQuery, callback_data: dict):
    '''Обработчик для добавления товара в корзину.'''

    await call.answer(text=f'{emojize(":robot:")} Добавляю товар в корзину.\nЗапрос к серверу...')
    item_id = callback_data.get('item_id')
    user_tlg_id = call.from_user.id
    await add_item_in_basket(user_tlg_id=user_tlg_id, item_id=item_id)


async def you_are_in_basket(message: types.Message):
    '''Обработчик для перехода в корзину по реплай кнопке.'''

    await message.answer(f'{emojize(":robot:")} Раздел КОРЗИНА {emojize(":wastebasket:")}', reply_markup=BASKET_KEYBRD)
    user_tlg_id = message.from_user.id
    chat_id = message.chat.id
    response = await get_user_basket(user_tlg_id)

    for i_elem in response:
        item_id = i_elem[0]
        item_name = i_elem[1]
        items_numbers_in_basket = i_elem[3]
        total_price = round(i_elem[2] * items_numbers_in_basket, 2)
        text_for_message = f'{emojize(":bookmark:")}Название товара: {item_name}\n' \
                           f'{emojize(":input_numbers:")}Количество: {items_numbers_in_basket} шт.\n' \
                           f'{emojize(":money_with_wings:")}Итоговая цена позиции: {total_price} руб.'
        i_message = await message.answer(text=text_for_message)
        inline_keyboard = basket_formation_inline(i_message.message_id, user_tlg_id, item_id, items_numbers_in_basket,
                                                  chat_id)
        await i_message.edit_text(text=text_for_message, reply_markup=inline_keyboard)


async def change_items_in_basket(call: CallbackQuery, callback_data: dict):
    '''Обработчик для изменения количества товаров в корзине.'''

    await call.answer(text=f'{emojize(":robot:")} Редактирую корзину.\nЗапрос к серверу...')
    # сперва изменяем кол-во товаров в БД
    user_tlg_id = callback_data['user_tlg_id']
    item_id = callback_data['item_id']
    flag = callback_data['req_flag']
    chat_id = callback_data.get('chat_id')
    message_id = callback_data.get('message_id')
    if flag == 'plus':
        change_response = await add_item_in_basket(user_tlg_id, item_id)
        # если получили ответом статус==204, то выходим из функции
        if change_response == 204:
            await call.answer(text=f'{emojize(":robot:")}Товара закончился...', show_alert=True)
            return
    elif flag == 'minus':
        change_response = await remove_item_from_basket(user_tlg_id, item_id)
        # если получили ответом статус==204, то выходим из функции
        if change_response == 204:
            # удаляем сообщение с товаром и информируем пользователя
            await BOT.delete_message(chat_id=chat_id, message_id=message_id)
            await call.answer(text=f'{emojize(":robot:")}Товар удалён из корзины...', show_alert=True)
            return

    # теперь делаем заново запрос на получение нужного товара из корзины
    result_response = await get_user_basket(user_tlg_id, item_id)
    items_numbers_in_basket = result_response[0][3]
    item_name = result_response[0][1]
    total_price = result_response[0][2] * items_numbers_in_basket
    text_for_message = f'{emojize(":bookmark:")}Название товара: {item_name}\n' \
                       f'{emojize(":input_numbers:")}Количество: {items_numbers_in_basket} шт.\n' \
                       f'{emojize(":money_with_wings:")}Итоговая цена позиции: {total_price} руб.'
    inline_keyboard = basket_formation_inline(message_id, user_tlg_id, item_id, items_numbers_in_basket, chat_id)
    await BOT.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=inline_keyboard, text=text_for_message)


async def clear_the_basket(message: types.Message):
    '''Обработчик для очистки корзины'''

    aphorizm_lst = [
        'Самая чистая и простая любовь — это любовь к еде.',
        'Меня не будут удивлять новые технологии до тех пор, пока я не смогу скачивать себе еду.',
        'Чаще аппетит приходит во время отсутствия еды.',
        'Назло врагам, съешь ужин сам.',
        'Потребность в пище сильнее любви.',
        'Поел — сердцем подобрел.',
        'Когда сомневаешься — ешь.',
        'Все на свете приедается, кроме еды.',
        'Если долго сидеть на диете, можно слечь.',
        'Когда тебе грустно, вкусная еда — наилучшее средство для поднятия настроения.',
        'Еда — это страсть. Еда — это любовь. Еда — это жизнь для каждого человека.',
    ]

    user_tlg_id = message.from_user.id
    response = await clear_basket(user_tlg_id)
    if response == 200:
        text_for_message = f'{emojize(":robot:")}Ваша корзина очищена...\n' \
                           f'{emojize(":pizza:")}Давайте добавим в неё что-нибудь вкусное.\n\n' \
                           f'{emojize(":robot:")}{emojize(":pinched_fingers:")}{random.choice(aphorizm_lst)}'
        await message.answer(text=text_for_message)
    else:
        await message.answer(text=f'{emojize(":robot:")}Проблемы с сервером...Не удалось выполнить запрос.')


def register_basket_handlers():
    '''Функция для регистрации обработчиков корзины товаров.'''

    DP.register_callback_query_handler(add_item_to_basket,
                                       callback_for_add_item_to_basket.filter(flag='add_item_to_basket_from_detail'))
    DP.register_message_handler(you_are_in_basket, Text(equals=KEYBOARD['BASKET']))
    DP.register_callback_query_handler(change_items_in_basket, callback_for_minus_plus_button.filter(handler_flag='change_in_basket'))
    DP.register_message_handler(clear_the_basket, Text(equals=KEYBOARD['X_BASKET']))
