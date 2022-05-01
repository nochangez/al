# coding=utf-8


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import tor_link, channel_link


support_keyboard = InlineKeyboardMarkup()

tor_button = InlineKeyboardButton("🥷 Магазин в TOR", url=tor_link)
channel_button = InlineKeyboardButton("🤠 Канал магазина", url=channel_link)

support_keyboard.add(tor_button).add(channel_button)
