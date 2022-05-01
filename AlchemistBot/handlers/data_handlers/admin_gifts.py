# coding=utf-8


from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from keyboards.reply_keyboards.menu import *
from keyboards.inline_keyboards.admin import *
from keyboards.reply_keyboards.back_admin import *
from services.project.gifts_controller import GiftsController


gifts_controller = GiftsController()


class UpdateGiftState(StatesGroup):
    waiting_for_gift = State()
    waiting_for_coordinates = State()


class DeleteGiftState(StatesGroup):
    waiting_for_accept = State()


async def update_gift(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    await message.edit_text("<b>Обновление раздачи</b>")
    await message.answer("🪨 <b>Введите текст для раздачи клада</b>\n\n"
                         "<code>Чтобы отменить обновление раздачи, нажмите на кнопку</code> "
                         "<b>Отменить</b>", reply_markup=back_admin_keyboard)

    await UpdateGiftState.waiting_for_gift.set()


async def update_gift_choosing(message: types.Message, state: FSMContext):
    gift_text = message.text

    if gift_text != "Отменить":
        await redis_helper.redis_set("gift_text", gift_text)
        await message.answer("✅ <b>Текст раздачи сохранен</b>")

        await message.answer("🧭 <b>Введите текст для координат раздачи</b>\n\n"
                             "<code>Чтобы отменить обновление раздачи, "
                             "нажмите на кнопку</code> <b>Отменить</b>", reply_markup=back_admin_keyboard)

        await UpdateGiftState.next()
    else:
        await message.answer("⚠ <b>Обновление раздачи отменено</b>", reply=admin_keyboard)
        await state.finish()


async def update_gift_coordinates_choosing(message: types.Message, state: FSMContext):
    coordinates_text = message.text

    if coordinates_text != "Отменить":
        await redis_helper.redis_set("coordinates_text", coordinates_text)
        await message.answer("✅ <b>Текст координат раздачи сохранен</b>")

        gift_text = str(await redis_helper.decode_bytes(
            await redis_helper.redis_get("gift_text")
        ))

        await gifts_controller.update_gift(gift_text, coordinates_text)

        await message.answer("✅ <b>Раздача обновлена</b>")
        await message.answer(f"🪨 <b>Раздача клада в твоем городе:</b>\n\n"
                             f"{gift_text}\n\n\n"
                             f"🧭 <b>Координаты раздачи:</b>\n\n"
                             f"{coordinates_text}", reply_markup=menu_keyboard)
    else:
        await redis_helper.redis_delete("gift_text")

        await message.answer("⚠ <b>Обновление раздачи отменено</b>", reply_markup=admin_keyboard)
        await state.finish()

    await state.finish()


async def del_gift(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    await message.edit_text("<b>Удаление раздачи</b>")

    if len(await gifts_controller.get_gift_info()) != 0:
        accept_keyboard = types.InlineKeyboardMarkup()

        no_button = types.InlineKeyboardButton("Нет", callback_data="delete_gift_no")
        yes_button = types.InlineKeyboardButton("Да", callback_data="delete_gift_yes")

        accept_keyboard.add(yes_button, no_button)

        await message.answer("❗️ <b>Вы подтрвеждаете удаление раздачи?</b>", reply_markup=accept_keyboard)

        await DeleteGiftState.waiting_for_accept.set()
    else:
        await message.edit_text("⚠ <b>Раздач пока что нет</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()


async def del_gift_accepting(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    accepting = callback_query.data.replace("delete_gift_", '')

    await callback_query.answer("Подтверждение...")

    if accepting in ('yes', 'no'):
        if accepting == "yes":
            await gifts_controller.delete_gift()
            await message.edit_text("✅ <b>Раздача удалена</b>", reply_markup=admin_keyboard)

            await state.finish()
        else:
            await message.edit_text("⚠ <b>Удаление раздачи отменено</b>", reply_markup=admin_keyboard)
            await state.finish()

    await state.finish()


async def show_gift(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка раздачи...")

    gift_info = await gifts_controller.get_gift_info()

    if len(gift_info) != 0:
        gift_info = gift_info[0]

        gift = gift_info[0]
        coordinates = gift_info[1]

        await message.edit_text(f"<b>Раздача:</b>\n\n{gift}\n\n\n"
                                f"<b>Координаты:</b>\n\n{coordinates}")
        await message.answer("<b>Раздача загружена</b>", reply_markup=menu_keyboard)
    else:
        await message.edit_text("⚠ <b>Раздач пока что нет</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)


def register_handlers_admin_gifts(dp: Dispatcher):
    dp.register_callback_query_handler(
        update_gift,
        lambda callback_query: callback_query.data and callback_query.data == "admin_gift_update",
        state=None
    )
    dp.register_message_handler(
        update_gift_choosing,
        content_types=['text'], state=UpdateGiftState.waiting_for_gift
    )
    dp.register_message_handler(
        update_gift_coordinates_choosing,
        content_types=['text'], state=UpdateGiftState.waiting_for_coordinates
    )
    dp.register_callback_query_handler(
        del_gift,
        lambda callback_query: callback_query.data and callback_query.data == "admin_gift_del",
        state=None
    )
    dp.register_callback_query_handler(
        del_gift_accepting,
        lambda callback_query: callback_query.data and callback_query.data.startswith("delete_gift_"),
        state=DeleteGiftState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        show_gift,
        lambda callback_query: callback_query.data and callback_query.data == "admin_gift_get"
    )
