# coding=utf-8


from aiogram import Dispatcher, types

from keyboards.reply_keyboards.menu import *
from services.project.user_controller import UserController


user_controller = UserController()


async def choose_city(callback_query: types.CallbackQuery):
    message = callback_query.message
    user_id = callback_query.from_user.id
    city = callback_query.data.replace('city_', '')

    for i in range(100):
        print(user_id, city)
    await message.edit_text(f"Выбран город: <b>{city}</b>")
    await user_controller.add_user(user_id=user_id, city=city)

    welcome_message = "🧪 Добро пожаловать в <b>Алхимик SHOP</b> ✨\n\n" \
                      "🌈 Только мы <u>раздаем бесплатно</u> клад 🔥"

    await message.answer(welcome_message, reply_markup=menu_keyboard)


def register_handlers_choose_city(dp: Dispatcher):
    dp.register_callback_query_handler(
        choose_city,
        lambda callback_query: callback_query.data and callback_query.data.startswith('city_')
    )
