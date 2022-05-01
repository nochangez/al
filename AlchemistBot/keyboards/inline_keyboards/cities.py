# coding=utf-8


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import init_cities


async def cities_keys_init():
    cities = await init_cities()

    cities_keyboard = InlineKeyboardMarkup()

    for city in cities:
        cities_keyboard.add(InlineKeyboardButton(city, callback_data=f"city_{city}"))

    return cities_keyboard
