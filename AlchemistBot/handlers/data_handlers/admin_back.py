# coding=utf-8


from aiogram import Dispatcher, types

from keyboards.reply_keyboards.menu import menu_keyboard


async def back_menu(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    await message.delete()
    await message.answer("👈 <b>Возврат в главное меню</b>", reply_markup=menu_keyboard)


def register_handlers_admin_back(dp: Dispatcher):
    dp.register_callback_query_handler(
        back_menu,
        lambda callback_query: callback_query.data and callback_query.data == "back_menu"
    )
