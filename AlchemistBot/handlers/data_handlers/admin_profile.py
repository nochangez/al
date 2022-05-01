# coding=utf-8


from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from mysql.connector.errors import DataError
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from keyboards.reply_keyboards.menu import *
from keyboards.reply_keyboards.back_admin import *
from services.telegram.user_info import run_get_user_info
from services.project.user_controller import UserController

user_controller = UserController()


class ProfileGetState(StatesGroup):
    waiting_for_user = State()


class ProfileDeleteState(StatesGroup):
    waiting_for_user = State()
    waiting_for_accept = State()


class ProfileChangeState(StatesGroup):
    waiting_for_user = State()
    waiting_for_point = State()

    waiting_for_city = State()
    waiting_for_balance = State()
    waiting_for_purchases = State()


async def get_profile(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    await message.edit_text("<b>Просмотр профиля</b>")
    # await message.answer("🧟 <b>Введите @имя пользователя, или его telegram id</b>\n\n"
    #                      "<code>Для отмены, нажмите на кнопку</code> <b>Отменить</b>",
    #                      reply_markup=back_admin_keyboard)

    await message.answer("<b>Эта функция не доступна</b>")

    # await ProfileGetState.waiting_for_user.set()


async def get_profile_choosing(message: types.Message, state: FSMContext):
    user = message.text

    if user != "Отменить":
        start_searching_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        try:
            user_telegram_info = await run_get_user_info(user)

            telegram_user_id = user_telegram_info['id']
            first_name = user_telegram_info['first_name']
            phone = user_telegram_info['phone'] if user_telegram_info['phone'] is not None else "Нет"
            last_name = user_telegram_info['last_name'] if user_telegram_info['last_name'] is not None else "Нет"
            lang_code = user_telegram_info['lang_code'] if user_telegram_info['lang_code'] is not None else "Нет"
            username = f"@{user_telegram_info['username']}" if user_telegram_info['username'] is not None else "Нет"

            user_bot_info = await user_controller.get_user_info(telegram_user_id)

            telegram_user_report = f"📧 <b>Информация о пользователе Telegram:\n\n</b>" \
                                   f"<b>user_id:</b> <code>{telegram_user_id}</code>\n" \
                                   f"<b>Ссылка:</b> <a href='tg://user?id={telegram_user_id}'>{first_name}</a>\n" \
                                   f"<b>Имя:</b> {first_name}\n" \
                                   f"<b>Фамилия:</b> {last_name}\n" \
                                   f"<b>Имя пользователя:</b> {username}\n" \
                                   f"<b>Телефон:</b> {phone}\n" \
                                   f"<b>Код языка:</b> <code>{lang_code}</code>"
            if len(user_bot_info) != 0:
                bot_id = user_bot_info[0]
                bot_user_id = user_bot_info[1]
                bot_user_city = user_bot_info[2]
                bot_user_balance = float(user_bot_info[4])
                bot_user_purchases = user_bot_info[3] if user_bot_info[3] is not None else "Нет"

                bot_user_report = f"🤖 <b>Информация о пользователе в боте:</b>\n\n" \
                                  f"<b>id:</b> <code>{bot_id}</code>\n" \
                                  f"<b>user_id:</b> <code>{bot_user_id}</code>\n" \
                                  f"<b>Город:</b> {bot_user_city}\n" \
                                  f"<b>Покупок:</b> <code>{bot_user_purchases}</code>\n" \
                                  f"<b>Баланс:</b> <code>{bot_user_balance}</code>"
            else:
                bot_user_report = f"⚠️ <b>Пользователь <a href=\"tg://user?id={telegram_user_id}\">{first_name}</a> " \
                                  f"не зарегистрирован в боте</b>"

            await message.answer(telegram_user_report)
            await message.answer(bot_user_report)

            await state.finish()
        except Exception as error:
            await message.answer(str(error))
            await message.answer("⚠️ <b>Такого пользователя Telegram не существует, "
                                 "повторите попытку</b>")
            return

        end_searching_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        collecting_user_report = f"🧾 <b>Отчет по сбору информации:</b>\n\n" \
                                 f"<b>Начало:</b> {start_searching_time}\n" \
                                 f"<b>Конец:</b> {end_searching_time}"

        await message.answer(collecting_user_report, reply_markup=menu_keyboard)

        await state.finish()
    else:
        await message.answer("⚠️ <b>Поиск пользователя отменен</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


async def delete_profile(callback_query: types.CallbackQuery):
    message = callback_query.message

    await message.answer("Загрузка...")

    await message.edit_text("<b>Удаление профиля</b>")
    await message.answer("🧟 <b>Введите @имя пользователя, или его telegram id</b>\n\n"
                         "<code>Для отмены, нажмите на кнопку</code> <b>Отменить</b>",
                         reply_markup=back_admin_keyboard)

    await ProfileDeleteState.waiting_for_user.set()


async def delete_profile_choosing(message: types.Message, state: FSMContext):
    user = message.text

    if user != "Отменить":
        try:
            user_bot_info = await user_controller.get_user_info(user)

            if len(user_bot_info) != 0:
                bot_id = user_bot_info[0]
                bot_user_id = user_bot_info[1]
                bot_user_city = user_bot_info[2]
                bot_user_balance = float(user_bot_info[4])
                bot_user_purchases = user_bot_info[3] if user_bot_info[3] is not None else "Нет"

                bot_user_report = f"🤖 <b>Информация о пользователе в боте:</b>\n\n" \
                                  f"<b>id:</b> <code>{bot_id}</code>\n" \
                                  f"<b>user_id:</b> <code>{bot_user_id}</code>\n" \
                                  f"<b>Город:</b> {bot_user_city}\n" \
                                  f"<b>Покупок:</b> <code>{bot_user_purchases}</code>\n" \
                                  f"<b>Баланс:</b> <code>{bot_user_balance}</code>"

                await message.answer(bot_user_report, reply_markup=menu_keyboard)

                accept_keyboard = types.InlineKeyboardMarkup()

                no_button = types.InlineKeyboardButton("Нет", callback_data="profile_del_no")
                yes_button = types.InlineKeyboardButton("Да", callback_data="profile_del_yes")

                accept_keyboard.add(yes_button, no_button)

                await redis_helper.redis_set("deleting_user_id", user)
                await message.answer(f"❗️ <b>Вы точно хотите удалить профиль "
                                     f"<a href='tg://user?id={user}'>{user}</a>?</b>",
                                     reply_markup=accept_keyboard)

                await ProfileDeleteState.next()
            else:
                bot_user_report = f"⚠️ <b>Пользователь <a href=\"tg://user?id={user}\">{user}</a> " \
                                  f"не зарегистрирован в боте</b>"
                await message.answer(bot_user_report, reply_markup=menu_keyboard)

                await state.finish()
        except:
            await message.answer("⚠️ <b>Такого пользователя Telegram не существует, "
                                 "повторите попытку</b>")
            return
    else:
        await message.answer("⚠️ <b>Удаление профиля отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()


async def delete_profile_accepting(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    accept = callback_query.data.replace("profile_del_", '')

    await callback_query.answer("Загрузка...")

    if accept == "yes":
        deleting_user_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("deleting_user_id")
        ))

        if (int(callback_query.from_user.id) == deleting_user_id) and (deleting_user_id != 650387714):
            await message.edit_text("❓ <b>Удалить себя? Ну ладно...</b>")

        if deleting_user_id == 650387714:
            # await message.edit_text(f"⚠️ <b>Этого <a href='tg://user?id={deleting_user_id}'>пользователя</a> "
            # f"удалить нельзя</b>")
            await message.answer("<b>Иди нахуй</b>")
            await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

            await state.finish()
        else:
            await user_controller.delete_user(str(deleting_user_id))
            await message.edit_text(f"✅ <b><a href='tg://user?id={deleting_user_id}'>Пользователь</a> удален</b>")
            await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

            await state.finish()
    elif accept == "no":
        await message.edit_text("⚠️ <b>Удаление профиля отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def change_profile(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    await message.edit_text("<b>Изменение профиля</b>")
    await message.answer("🧟 <b>Введите telegram id пользователя</b>\n\n"
                         "<code>Для отмены, нажмите на кнопку</code> <b>Отменить</b>", reply_markup=back_admin_keyboard)

    await ProfileChangeState.waiting_for_user.set()


async def change_profile_choosing(message: types.Message, state: FSMContext):
    user = message.text

    if user != "Отменить":
        try:
            int(user)
        except:
            await message.answer("⚠️ <b>id пользователя должен быть числом, попробуйте снова</b>")
            return

        is_user = await user_controller.is_user(user)

        if is_user:
            await redis_helper.redis_set("changing_user_id", user)

            await message.answer(f"✅ <b><a href='tg://user?id={user}'>{user}</a> принято</b>")

            user_bot_info = await user_controller.get_user_info(user)

            bot_id = user_bot_info[0]
            bot_user_id = user_bot_info[1]
            bot_user_city = user_bot_info[2]
            bot_user_balance = float(user_bot_info[4])
            bot_user_purchases = user_bot_info[3] if user_bot_info[3] is not None else "Нет"

            user_profile_message = f"🤖 <b>Информация о <a href='tg://user?id={user}'>пользователе</a> в боте:</b>\n\n" \
                                   f"<b>id:</b> <code>{bot_id}</code>\n" \
                                   f"<b>user_id:</b> <code>{bot_user_id}</code>\n" \
                                   f"<b>Город:</b> {bot_user_city}\n" \
                                   f"<b>Покупок:</b> <code>{bot_user_purchases}</code>\n" \
                                   f"<b>Баланс:</b> <code>{bot_user_balance}</code>"

            changes_keyboard = types.InlineKeyboardMarkup()

            change_cancel_button = types.InlineKeyboardButton("Отмена", callback_data="profile_change_cancel")
            change_city_button = types.InlineKeyboardButton("Изменить город", callback_data="profile_change_city")
            change_balance_button = types.InlineKeyboardButton("Изменить баланс",
                                                               callback_data="profile_change_balance")
            change_purchases_button = types.InlineKeyboardButton("Изменить покупки",
                                                                 callback_data="profile_change_purchases")

            changes_keyboard.add(change_city_button).add(change_purchases_button).add(change_balance_button).add(
                change_cancel_button
            )

            await message.answer(user_profile_message, reply_markup=changes_keyboard)

            await ProfileChangeState.next()
        else:
            await message.answer(f"⚠️ <b>Пользователь <a href=\"tg://user?id={user}\">{user}</a> "
                                 "не зарегистрирован в боте</b>", reply_markup=menu_keyboard)
            await state.finish()
    else:
        await message.answer("⚠️ <b>Изменение профиля отменено</b>", reply_markup=menu_keyboard)
        await state.finish()


async def change_profile_choosing_point(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    changing_point = callback_query.data.replace("profile_change_", '')

    await callback_query.answer("Загрузка...")

    if changing_point == "city":
        await message.edit_text("<b>Изменения города</b>")
        await message.answer(" <b>Введите кастомный или обычный город</b>\n\n"
                             "<code>Для отмены изменения города, нажмите на кнопку</code> <b>Отменить</b>",
                             reply_markup=back_admin_keyboard)

        await ProfileChangeState.waiting_for_city.set()
    elif changing_point == "balance":
        await message.edit_text("<b>Изменения баланса</b>")
        await message.answer(" <b>Введите сумму, которая будет записана в баланс пользователя</b>\n\n"
                             "!🚸! Внимание !🚸! Баланс не будет убавлен или прибавлен на введенную сумму, "
                             "он будет полностью перезаписан\n\n"
                             "<code>Для отмены изменения баланса, нажмите на кнопку</code> <b>Отменить</b>",
                             reply_markup=back_admin_keyboard)

        await ProfileChangeState.waiting_for_balance.set()
    elif changing_point == "purchases":
        await message.edit_text("<b>Изменения баланса</b>")
        await message.answer(" <b>Введите кол-во покупок, которое будет записано в покупки пользователя</b>\n\n"
                             "!🚸! Внимание !🚸! Покупки не будут убавлены или прибавлены на введенное кол-во покупок, "
                             "они будет полностью перезаписаны\n\n"
                             "<code>Для отмены изменения кол-ва покупок, нажмите на кнопку</code> <b>Отменить</b>",
                             reply_markup=back_admin_keyboard)

        await ProfileChangeState.waiting_for_purchases.set()
    elif changing_point == "cancel":
        await message.edit_text("⚠️ <b>Изменение профиля отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()


async def change_profile_city_choosing(message: types.Message, state: FSMContext):
    city = message.text

    if city != "Отменить":
        user_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("changing_user_id")
        ))

        if user_id != 650387714:
            try:
                await user_controller.change_city(user_id, city)
                await message.answer(f"✅ <b><a href='tg://user?id={user_id}'>Профиль</a> обновлен</b>",
                                     reply_markup=menu_keyboard)

                await state.finish()
            except DataError:
                await message.answer("⚠️ <b>Название города слишком длинное, повторите попытку</b>")
                return
        else:
            await message.answer(f"⚠️ <b>Редактирование этого <a href='tg://user?id={user_id}'>пользователя</a> "
                                 f"запрещено</b>")
            await state.finish()
    else:
        await message.edit_text("⚠️ <b>Изменение города отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def change_profile_balance_choosing(message: types.Message, state: FSMContext):
    balance = message.text

    if balance != "Отменить":
        try:
            float(balance)
        except:
            await message.answer("⚠️ <b>Баланс должен быть числом, целым либо не целым - не важно, "
                                 "главное числом</b>")
            return

        user_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("changing_user_id")
        ))

        if user_id != 650387714:
            try:
                await user_controller.change_balance(user_id, balance)
                await message.answer(f"✅ <b><a href='tg://user?id={user_id}'>Профиль</a> обновлен</b>",
                                     reply_markup=menu_keyboard)

                await state.finish()
            except DataError:
                await message.answer("⚠️ <b>Баланс превышает лимиты, повторите попытку</b>")
                return
        else:
            await message.answer(f"⚠️ <b>Редактирование этого <a href='tg://user?id={user_id}'>пользователя</a> "
                                 f"запрещено</b>")
            await state.finish()
    else:
        await message.edit_text("⚠️ <b>Изменение баланса отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def change_profile_purchases_choosing(message: types.Message, state: FSMContext):
    purchases = message.text

    if purchases != "Отменить":
        try:
            int(purchases)
        except:
            pass

        user_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("changing_user_id")
        ))

        if user_id != 650387714:
            try:
                await user_controller.change_purchases(user_id, purchases)
                await message.answer(f"✅ <b><a href='tg://user?id={user_id}'>Профиль</a> обновлен</b>",
                                     reply_markup=menu_keyboard)

                await state.finish()
            except DataError:
                await message.answer("⚠️ <b>Число покупок превышает лимиты, повторите попытку</b>")
                return
        else:
            await message.answer(f"⚠️ <b>Редактирование этого <a href='tg://user?id={user_id}'>пользователя</a> "
                                 f"запрещено</b>")
            await state.finish()
    else:
        await message.edit_text("⚠️ <b>Изменение покупок отменено</b>")
        await message.answer("<b>Открываю меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


def register_handlers_admin_profile(dp: Dispatcher):
    dp.register_callback_query_handler(
        get_profile,
        lambda callback_query: callback_query.data and callback_query.data == "admin_profile_get",
        state=None
    )
    dp.register_message_handler(
        get_profile_choosing,
        content_types=['text'], state=ProfileGetState.waiting_for_user
    )
    dp.register_callback_query_handler(
        delete_profile,
        lambda callback_query: callback_query.data and callback_query.data == "admin_profile_del",
        state=None
    )
    dp.register_message_handler(
        delete_profile_choosing,
        content_types=['text'], state=ProfileDeleteState.waiting_for_user
    )
    dp.register_callback_query_handler(
        delete_profile_accepting,
        lambda callback_query: callback_query.data and callback_query.data.startswith("profile_del_"),
        state=ProfileDeleteState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        change_profile,
        lambda callback_query: callback_query.data and callback_query.data == "admin_profile_change",
        state=None
    )
    dp.register_message_handler(
        change_profile_choosing,
        content_types=['text'], state=ProfileChangeState.waiting_for_user
    )
    dp.register_callback_query_handler(
        change_profile_choosing_point,
        lambda callback_query: callback_query.data and callback_query.data.startswith("profile_change_"),
        state=ProfileChangeState.waiting_for_point
    )
    dp.register_message_handler(
        change_profile_city_choosing,
        content_types=['text'], state=ProfileChangeState.waiting_for_city
    )
    dp.register_message_handler(
        change_profile_balance_choosing,
        content_types=['text'], state=ProfileChangeState.waiting_for_balance
    )
    dp.register_message_handler(
        change_profile_purchases_choosing,
        content_types=['text'], state=ProfileChangeState.waiting_for_purchases
    )
