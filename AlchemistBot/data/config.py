# coding=utf-8


import os

from aiogram import Bot, Dispatcher, types

from data.services.redis_helper import RedisHelper
from services.project.cities_controller import CitiesController


# TOKENS
tokens = {
    'qiwi_token': os.getenv('qiwiSecretTokenA'),
    'telegram_token': os.getenv('telegramTokenA'),
}  # set tokens


# IDS
admins = [650387714, 387869905, 5393265384]  # admins
channel_id = -1001693018362  # channel id -


# PATHS
path_to_data = "/Users/nochanga/PycharmProjects/AlchemistBot/data/"
path_to_config_files = "/Users/nochanga/PycharmProjects/AlchemistBot/data/config_files/"


# TELEGRAM CLIENT DATA
api_id = 10306109
api_hash = "d5b67f35fdf8db7ef606b851f34b22df"


# CITIES
async def init_cities():
    cities = []

    cities_controller = CitiesController()
    cities_db = await cities_controller.get_cities()

    for city in cities_db:
        city_name = city[1]
        cities.append(city_name)

    return cities


# LINKS
tor_link = "https://t.me/+CsmX4dSgKH04Njli"  # tor link for support
channel_link = "https://t.me/alhimik_link"  # invite channel link for support


# CALLABLE
redis_helper = RedisHelper()
bot = Bot(token=tokens['telegram_token'], parse_mode=types.ParseMode.HTML)  # init bot
dispatcher = Dispatcher(bot, storage=redis_helper.redis_storage)
