# coding=utf-8


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

gifts_button = KeyboardButton("🎁 Раздача товара")
goods_button = KeyboardButton("🪨 Товар")
profile_button = KeyboardButton("👨🏻‍💻 Мой аккаунт")
support_button = KeyboardButton("🛎 Связь")

menu_keyboard.add(profile_button, goods_button).add(support_button, gifts_button)
