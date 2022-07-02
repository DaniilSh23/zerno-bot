from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import post_req_for_add_new_user
from keyboards.callback_data_bot import callback_for_headpage
from keyboards.inline_keyboard import inline_keyboard_for_admins
from keyboards.reply_keyboard import MAIN_MENU
from settings.config import KEYBOARD, DP, BOT, STAFF_ID


async def head_page(message: types.Message):
    '''Обработчик для главного меню бота, команда start, help'''

    user_data = {
        'user_tlg_id': message.from_user.id,
        'user_tlg_name': message.from_user.username
    }
    if message.from_user.first_name:
        user_name = message.from_user.first_name
        user_data['user_name'] = user_name
    response = await post_req_for_add_new_user(user_data)
    if response:
        await message.answer(
            emojize(':cup_with_straw:Добро пожаловать в кафе.'
                    '\nЭтот бот поможет Вам посмотреть меню, '
                    'оформить заказ, выбрать доставку и оплатить.'),
            reply_markup=MAIN_MENU)
    else:
        await message.answer(
            emojize(':robot: У бота что-то барохлит...:('
                    '\n:construction_worker: Мы уже разбираемся, '
                    'скоро он будет как новенький.:OK_hand:'),
            reply_markup=MAIN_MENU)


async def return_to_heade_page(message: types.Message):
    '''Реакция бота на нажатие кнопки ГЛАВНАЯ'''

    await message.answer(f'Вы перешли к главному меню', reply_markup=MAIN_MENU)

    if message.from_user.id in STAFF_ID:
        inline_keyboard = inline_keyboard_for_admins()
        await message.answer(text=f'Админ панель', reply_markup=inline_keyboard)


async def send_media_id(message: types.Message):
    '''Обработчик для отправки ID присланного боту файла'''

    # if message.from_user.id in ADMINS_ID_LST:
    #     await BOT.send_message(
    #         chat_id=message.from_user.id,
    #         text=f'ID файла: {message.photo[-1].file_id}'
    #     )
    await BOT.send_message(
        chat_id=message.from_user.id,
        text=f'ID файла: {message.photo[-1].file_id}'
    )


async def about_cafe(message: types.Message):
    '''Обработчик для раздела о магазине'''

    text_about_cafe = f'{emojize(":fork_and_knife_with_plate:")}<b><ins>Ваше уникальное название заведения</ins></b>\n' \
                      f'{emojize(":four_o’clock:")}<ins>Режим работы:</ins> 08:00 - 23:00\n' \
                      f'{emojize(":cityscape:")}<ins>Адрес:</ins> г.Изумрудный, ул. Железного Дровосека, 51\n' \
                      f'{emojize(":telephone_receiver:")}<ins>Контактый телефон:</ins> +7 777-77-23\n'
    await message.answer(text=text_about_cafe)


async def head_page_from_order(call: CallbackQuery):

    await call.answer(text='Главное меню')
    await call.message.answer(text='Вы перешли к главному меню.', reply_markup=MAIN_MENU)


def register_head_page_handlers():
    '''Функция для регистрации обработчиков'''

    DP.register_message_handler(head_page, Command(['start', 'home', ]))
    DP.register_message_handler(return_to_heade_page, Text(equals=[KEYBOARD['HEAD_PAGE']]))
    DP.register_message_handler(about_cafe, Text(equals=[KEYBOARD['INFO']]))
    DP.register_message_handler(send_media_id, content_types=types.ContentTypes.PHOTO)
    DP.register_callback_query_handler(head_page_from_order, callback_for_headpage.filter(flag='head'))
