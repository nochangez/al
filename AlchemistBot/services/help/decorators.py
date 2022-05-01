# coding=utf-8


from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from datetime import datetime

from data.config import admins, channel_id, bot
from keyboards.inline_keyboards.admin import admin_keyboard


def timeit(func):

    async def wrapper(callback_query: CallbackQuery):
        message = callback_query.message

        start_process_time = datetime.now()
        await message.answer(f"<b>start time is {start_process_time}</b>")

        func(callback_query)

        end_process_time = datetime.now()
        await message.answer(f"<b>end time is {end_process_time}</b>")

        return await func(callback_query)

    return wrapper


def auth(func):

    async def wrapper(message: Message):
        if message.from_user.id not in tuple(admins):
            await message.answer("<b>access denied</b>")
        return await func(message)

    return wrapper


def is_cancel(func):

    async def wrapper(message: Message, state: FSMContext):
        if message.text == "Отменить":
            await message.answer("⚠️ <b>Операция отменена</b>", reply_markup=admin_keyboard)
            return await state.finish()
        return await func(message, state)

    return wrapper


def is_subscriber(func):

    async def wrapper(message: Message, state: FSMContext = None):
        member_info = await bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)
        user_status = member_info['status']

        if user_status == "member":
            return await func(message, state) if state is not None else await func(message)
        else:
            sub_keyboard = types.InlineKeyboardMarkup()
            check_button = types.InlineKeyboardButton("Проверить подписку", callback_data="check_sub")
            sub_keyboard.add(check_button)

            return await message.answer("<b>Подпишитесь на канал @alhimik_link</b>", reply_markup=sub_keyboard)

    return wrapper
