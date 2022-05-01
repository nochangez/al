# coding=utf-8


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


top_up_keyboard = InlineKeyboardMarkup()

top_up_button = InlineKeyboardButton("📥 Пополнить баланс", callback_data="top_up_balance")

top_up_keyboard.add(top_up_button)
