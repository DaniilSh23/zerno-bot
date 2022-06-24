from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize
from aiogram import types

from another.request_to_API import get_items_categories, get_items_list, get_item_detail_info
from keyboards.callback_data_bot import callback_for_next_or_prev_button, callback_for_category, \
    callback_for_items_by_category, callback_back_to_categories
from keyboards.inline_keyboard import category_item_formation_keyboard, items_list_formation_keyboard, \
    item_detail_formation_inline
from keyboards.reply_keyboard import COMMON_KEYBRD
from settings.config import KEYBOARD, DP


async def items_categories(message: types.Message):
    '''Обработчик для раздела категорий товаров'''

    await message.answer(f'{emojize(":robot:")} Работаю с сервером...', reply_markup=COMMON_KEYBRD)
    # выполнить запрос к АПИ и получить результат запроса
    response = await get_items_categories()
    # передать результат запроса и другую необходимую инфу в формирователь клавиатуры
    inline_keyboard = category_item_formation_keyboard(response_data=response, message_id=message.message_id)
    # отправить пользователю клавиатуру
    await message.answer(text=f'{emojize(":robot:")} Доступны следующие категории', reply_markup=inline_keyboard)


async def pagination_step_for_items_categories(call: CallbackQuery, callback_data: dict):
    '''Обработчик для пролистывание категорий товаров.'''

    await call.answer(text=f'{emojize(":robot:")} Перелистываю страницу категорий...')
    pagination_step = callback_data.get('pagination_step')
    response = await get_items_categories(pagination_part_of_link=pagination_step)
    inline_keyboard = category_item_formation_keyboard(response_data=response, message_id=callback_data['message_id'])
    await call.message.edit_text(text=f'{emojize(":robot:")}Список категорий товаров.', reply_markup=inline_keyboard)


async def items_list(call: CallbackQuery, callback_data: dict):
    '''Обработчик для отображения списка товаров'''

    await call.answer(text=f'{emojize(":robot:")} Получаю список товаров у сервера...')
    response = await get_items_list(items_category_id=callback_data['category_id'])
    inline_keyboard = items_list_formation_keyboard(response_data=response, message_id=call.message.message_id)
    await call.message.delete()
    await call.message.answer(f'{emojize(":robot:")} Вот, что у нас есть:', reply_markup=inline_keyboard)


async def pagination_step_for_items_list(call: CallbackQuery, callback_data: dict):
    '''Обработчик для пролистывания категорий товаров.'''

    await call.answer(text=f'{emojize(":robot:")} Перелистываю страницу товаров...')
    pagination_step = callback_data['pagination_step']
    response = await get_items_list(pagination_part_of_link=pagination_step)
    inline_keyboard = items_list_formation_keyboard(response_data=response, message_id=callback_data['message_id'])
    await call.message.edit_text(text=f'{emojize(":robot:")}Список товаров.', reply_markup=inline_keyboard)


async def item_detail(call: CallbackQuery, callback_data: dict):
    '''Обработчик для детального отображения товаров.'''

    await call.answer(text=f'{emojize(":robot:")} Получаю детальную информацию о товаре у сервера...')
    response = await get_item_detail_info(item_id=callback_data['item_id'])

    item_id = response['id']
    items_name = response['items_name']
    description = response['description']
    price = response['price']
    image_for_items_id = response['image_for_items_id']
    items_category = response['items_category']

    inline_keyboard = item_detail_formation_inline(
        category_id=items_category,
        item_id=item_id,
        message_id=call.message.message_id
    )
    await call.message.edit_text('Присылаю клавиатуру', reply_markup=inline_keyboard)
    await call.message.delete()

    text_to_user = f'{emojize(":hamburger:")}Название: {items_name}\n' \
                   f'{emojize(":money_with_wings:")}Цена за шт.: {price} руб.\n' \
                   f'{emojize(":clipboard:")}Описание: {description}\n'

    if image_for_items_id:
        await call.message.answer_photo(photo=image_for_items_id, caption=text_to_user, reply_markup=inline_keyboard)
    else:
        await call.message.answer(text=text_to_user, reply_markup=inline_keyboard)


def register_items_menu_handlers():
    DP.register_message_handler(items_categories, Text(equals=KEYBOARD['CHOOSE_GOODS']))
    DP.register_callback_query_handler(pagination_step_for_items_categories, callback_for_next_or_prev_button.filter(flag='pagination_categories'))
    DP.register_callback_query_handler(pagination_step_for_items_categories, callback_back_to_categories.filter(flag='back_to_categories'))
    DP.register_callback_query_handler(pagination_step_for_items_list, callback_for_next_or_prev_button.filter(flag='pagination_items'))
    DP.register_callback_query_handler(items_list, callback_for_category.filter(flag='category_for_items'))
    DP.register_callback_query_handler(item_detail, callback_for_items_by_category.filter(flag='item_detail'))


