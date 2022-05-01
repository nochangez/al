# coding=utf-8


from aiogram import Dispatcher, types

from keyboards.reply_keyboards.back import *
from keyboards.inline_keyboards.support import *


async def support(message: types.Message):
    support_message = "🧙 <b>Нас можно найти тут</b> 👇"
    support_loaded_message = "🍕 <b>Контакты загружены успешно!</b>"

    await message.answer(support_loaded_message, reply_markup=back_keyboard)
    await message.answer(support_message, reply_markup=support_keyboard)


def register_handlers_support(dp: Dispatcher):
    dp.register_message_handler(support, lambda message: message.text and message.text == "🛎 Связь")
