# coding=utf-8


from asyncio import sleep
from datetime import datetime
from os import remove, listdir

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.reply_keyboards.menu import *
from keyboards.inline_keyboards.admin import *
from keyboards.reply_keyboards.back_admin import *
from services.project.user_controller import UserController
from data.config import redis_helper, path_to_config_files, bot
from services.project.mailing_controller import MailingController

user_controller = UserController()
mailing_controller = MailingController()


class MailingUpdateState(StatesGroup):
    waiting_for_mailing = State()


class MailingDeleteState(StatesGroup):
    waiting_for_accept = State()


class MailingStartState(StatesGroup):
    waiting_for_accept = State()


async def update_mailing(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    await message.edit_text("<b>Обновление рассылки</b>")
    await message.answer("🖍 <b>Введите текст рассылки</b>\n\n"
                         "<code>Для отмены обновления рассылки нажмите "
                         "на кнопку</code> <b>Отменить</b>", reply_markup=back_admin_keyboard)

    await MailingUpdateState.waiting_for_mailing.set()


async def update_mailing_choosing(message: types.Message, state: FSMContext):
    mailing = message.text

    if mailing != "Отменить":
        await mailing_controller.update_mailing(mailing)
        await message.answer("✅ <b>Рассылка обновлена</b>", reply_markup=menu_keyboard)

        await state.finish()
    else:
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)
        await message.answer("⚠️ <b>Обновление рассылки отменено</b>", reply_markup=admin_keyboard)
        await state.finish()

    await state.finish()


async def delete_mailing(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    mailing = await mailing_controller.get_mailing()

    if len(mailing) != 0:
        accept_keyboard = InlineKeyboardMarkup()

        no_button = InlineKeyboardButton("Нет", callback_data="delete_mailing_no")
        yes_button = InlineKeyboardButton("Да", callback_data="delete_mailing_yes")

        accept_keyboard.add(yes_button, no_button)

        await message.edit_text("❗️ <b>Вы точно хотите удалить рассылку?</b>", reply_markup=accept_keyboard)

        await MailingDeleteState.waiting_for_accept.set()
    else:
        await message.edit_text("<b>Удаление рассылки</b>")
        await message.answer("⚠️ <b>Рассылка пока что не задана</b>", reply_markup=menu_keyboard)

        await state.finish()


async def delete_mailing_accepting(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    accept = callback_query.data.replace("delete_mailing_", '')

    await callback_query.answer("Подтверждение удаления...")

    if accept == "yes":
        await mailing_controller.del_mailing()

        await message.edit_text("✅ <b>Рассылка удалена</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()
    elif accept == "no":
        await message.edit_text("⚠️ <b>Удаление рассылки отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def start_mailing(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    mailing = await mailing_controller.get_mailing()

    if len(mailing) != 0:
        mailing_text = mailing[0][0]

        await redis_helper.redis_set("mailing", mailing_text)

        await message.answer("<b>Рассылка загружена</b>", reply_markup=menu_keyboard)
        await message.edit_text(f"📰 <b>Рассылка:</b>\n\n"
                                f"{mailing_text}")

        accept_keyboard = InlineKeyboardMarkup()

        no_button = InlineKeyboardButton("Нет", callback_data="start_mailing_no")
        yes_button = InlineKeyboardButton("Да", callback_data="start_mailing_yes")

        accept_keyboard.add(yes_button, no_button)

        await message.answer("❗️ <b>Вы точно хотите запустить эту рассылку?</b>", reply_markup=accept_keyboard)

        await MailingStartState.waiting_for_accept.set()
    else:
        await message.edit_text("<b>Запуск рассылки</b>")
        await message.answer("⚠️ <b>Рассылка пока что не задана</b>", reply_markup=menu_keyboard)

        await state.finish()


async def start_mailing_accepting(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    accept = callback_query.data.replace("start_mailing_", '')

    await callback_query.answer("Подтверждение запуска...")

    if accept == "yes":
        mailing = str(await redis_helper.decode_bytes(
            await redis_helper.redis_get("mailing")
        ))

        await message.edit_text("🚀 <b>Рассылка начинается...</b>\n\n"
                                "<code>Бот не будет доступен для Вас некоторое "
                                "время :( Я уведомлю, когда рассылка закончится</code>")

        start_mailing_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        remove(f"{path_to_config_files}Отчет - рассылка.txt") if \
            "Отчет - рассылка.txt" in listdir(path_to_config_files) else None

        mailing_report_file = open(f"{path_to_config_files}Отчет - рассылка.txt", 'w+', encoding='utf-8')
        mailing_report_file.close()

        users = [user[1] for user in await user_controller.get_users()]
        for user in users:
            try:
                await bot.send_message(user, mailing)

                with open(f"{path_to_config_files}Отчет - рассылка.txt", 'a+', encoding='utf-8') as mailing_report_file:
                    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    success_message = "Статус: ✅\n" \
                                      f"Получатель: {user}\n" \
                                      f"Дата: {current_time}\n\n" \
                                      f"###################################\n\n"

                    mailing_report_file.write(success_message)
            except Exception as sending_error:
                with open(f"{path_to_config_files}Отчет - рассылка.txt", 'a+', encoding='utf-8') as mailing_report_file:
                    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    failure_message = "Статус: ❌\n" \
                                      f"Получатель: {user}\n" \
                                      f"Причина: {sending_error}\n" \
                                      f"Дата: {current_time}\n\n" \
                                      f"###################################\n\n"

                    mailing_report_file.write(failure_message)

                    continue

            await sleep(0.3)

        end_mailing_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        await bot.send_document(
            callback_query.from_user.id,
            document=open(f"{path_to_config_files}Отчет - рассылка.txt"),
            caption="✅ <b>Рассылка закончена</b>\n\n"
                    f"<b>Начало:</b> {start_mailing_date}\n"
                    f"<b>Конец:</b> {end_mailing_date}\n\n"
                    "<code>Прикрепляю отчет по рассылке</code>"
        )

        await state.finish()
    elif accept == "no":
        await message.edit_text("⚠️ <b>Запуск рассылки отменен</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def get_mailing(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка рассылки...")

    mailing = await mailing_controller.get_mailing()

    if len(mailing) != 0:
        mailing_text = mailing[0][0]

        await message.answer("<b>Рассылка загружена</b>", reply_markup=menu_keyboard)
        await message.edit_text(f"📰 <b>Рассылка:</b>\n\n"
                                f"{mailing_text}")
    else:
        await message.edit_text("<b>Просмотр рассылки</b>")
        await message.answer("⚠️ <b>Рассылка пока что не задана</b>", reply_markup=menu_keyboard)


def register_handlers_admin_mailing(dp: Dispatcher):
    dp.register_callback_query_handler(
        update_mailing,
        lambda callback_query: callback_query.data and callback_query.data == "admin_mailing_update",
        state=None
    )
    dp.register_message_handler(
        update_mailing_choosing,
        content_types=['text'], state=MailingUpdateState.waiting_for_mailing
    )
    dp.register_callback_query_handler(
        delete_mailing,
        lambda callback_query: callback_query.data and callback_query.data == "admin_mailing_del",
        state=None
    )
    dp.register_callback_query_handler(
        delete_mailing_accepting,
        lambda callback_query: callback_query.data and callback_query.data.startswith("delete_mailing_"),
        state=MailingDeleteState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        start_mailing,
        lambda callback_query: callback_query.data and callback_query.data == "admin_mailing_start",
        state=None
    )
    dp.register_callback_query_handler(
        start_mailing_accepting,
        lambda callback_query: callback_query.data and callback_query.data.startswith("start_mailing_"),
        state=MailingStartState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        get_mailing,
        lambda callback_query: callback_query.data and callback_query.data == "admin_mailing_get"
    )
