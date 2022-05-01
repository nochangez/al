# coding=utf-8


from aiogram import types


accept_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

no_button = types.KeyboardButton("Нет")
yes_button = types.KeyboardButton("Да")

accept_keyboard.add(yes_button, no_button)
