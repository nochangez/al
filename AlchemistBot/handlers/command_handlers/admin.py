# coding=utf-8

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from data.config import admins
from keyboards.inline_keyboards.admin import *


async def process_admin_command(message: types.Message):
    if message.from_user.id in admins:
        await message.answer("<b>Отмена состояний и удаление клавиатур: "
                             "<i>выполнено</i></b>", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("<b>Открыл панель администратора:</b>", reply_markup=admin_keyboard)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(process_admin_command, commands=['admin'])
    dp.register_message_handler(process_admin_command, Text(equals="Отменить"))
