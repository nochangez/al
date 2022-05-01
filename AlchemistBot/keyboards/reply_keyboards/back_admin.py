# coding=utf-8


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


back_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

back_admin_button = KeyboardButton("Отменить")

back_admin_keyboard.add(back_admin_button)
