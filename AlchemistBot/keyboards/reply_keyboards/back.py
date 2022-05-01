# coding=utf-8


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

back_button = KeyboardButton("🏡 Вернуться в меню")

back_keyboard.add(back_button)
