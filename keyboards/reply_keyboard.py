from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from settings.config import KEYBOARD


'''Клавиатура главного меню'''
MAIN_MENU = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text=KEYBOARD['CHOOSE_GOODS'])
        ],
        [
            KeyboardButton(text=KEYBOARD['BASKET']),
            KeyboardButton(text=KEYBOARD['MY_ORDER']),
        ],
        [
            KeyboardButton(text=KEYBOARD['INFO'])
        ],
    ],
    resize_keyboard=True    # это, чтобы клавиатура не занимала пол экрана
)

'''Клавиатура для корзины'''
BASKET_KEYBRD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text=KEYBOARD['MAKE_AN_ORDER']),
        ],
        [
            KeyboardButton(text=KEYBOARD['HEAD_PAGE']),
            KeyboardButton(text=KEYBOARD['CHOOSE_GOODS']),
        ],
        [
            KeyboardButton(text=KEYBOARD['X_BASKET']),
        ]
    ],
    resize_keyboard=True    # это, чтобы клавиатура не занимала пол экрана
)

'''Клавиатура для раздела заказа'''
ORDER_KEYBRD = ReplyKeyboardMarkup(
    [
        # [
        #     KeyboardButton(text=KEYBOARD['MY_ORDER']),
        # ],
        [
            KeyboardButton(text=KEYBOARD['CHOOSE_GOODS']),
        ],
        [
            KeyboardButton(text=KEYBOARD['HEAD_PAGE']),
        ],
    ],
    resize_keyboard=True
)

'''Клавиатура для навигации в других разделах'''
COMMON_KEYBRD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text=KEYBOARD['CHOOSE_GOODS']),
        ],
        [
            KeyboardButton(text=KEYBOARD['HEAD_PAGE']),
            KeyboardButton(text=KEYBOARD['BASKET']),
        ],
    ],
    resize_keyboard=True
)
