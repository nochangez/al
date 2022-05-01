# coding=utf-8


from aiogram import Dispatcher, types

from data.config import channel_id, bot
from keyboards.reply_keyboards.menu import menu_keyboard


async def is_sub(message: types.Message, user_id: int):
    member_info = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return member_info['status']


async def check_sub(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Проверка профиля...")

    user_status = await is_sub(message, callback_query.from_user.id)

    if user_status != "member":
        await message.answer("❌ <b>Вы не подписались</b>")
    elif user_status == "member":
        await message.edit_text("✅ <b>Успешно</b>")
        await message.answer("🧪 Добро пожаловать в <b>Алхимик SHOP</b> ✨\n\n"
                             "🌈 Только мы <u>раздаем бесплатно</u> клад 🔥", reply_markup=menu_keyboard)


def register_handlers_check_sub(dp: Dispatcher):
    dp.register_callback_query_handler(
        check_sub,
        lambda callback_query: callback_query.data and callback_query.data == "check_sub"
    )
