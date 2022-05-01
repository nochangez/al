# coding=utf-8


from aiogram import Dispatcher, types

from keyboards.reply_keyboards.back import *
from services.project.user_controller import UserController
from keyboards.inline_keyboards.top_up_balance import top_up_keyboard


user_controller = UserController()


async def my_account(message: types.Message):
    user_id = message.from_user.id
    is_user = await user_controller.is_user(user_id)

    if is_user:
        user_info = await user_controller.get_user_info(user_id)

        city: str = user_info[2]
        purchases: int = user_info[3]
        balance: float = user_info[-1]

        my_account_message = f"🧚‍♂️ Аккаунт <b>{message.from_user.first_name}</b>\n\n" \
                             f"🪨 <b>Совершено покупок</b>: {purchases}\n" \
                             "🏷 <b>Личная скидка</b>: 0%\n" \
                             f"🌆 <b>Ваш город</b>: {city}\n" \
                             f"💰 <b>Баланс аккаунта</b>: {balance}₽\n" \

        await message.answer("🧙 <b>‍Алхимик SHOP</b> – дарит радость людям!", reply_markup=back_keyboard)
        await message.answer(my_account_message, reply_markup=top_up_keyboard)
    else:
        not_user_message = f"⚠️ <b>{message.from_user.first_name}</b>, " \
                           f"Вы пока что <u>не зарегистрированы</u>!\n\n" \
                           f"<code>Пройти регистрацию можно по команде</code> /start"
        await message.answer(not_user_message)


def register_handlers_my_account(dp: Dispatcher):
    dp.register_message_handler(my_account, lambda message: message.text and message.text == "👨🏻‍💻 Мой аккаунт")
