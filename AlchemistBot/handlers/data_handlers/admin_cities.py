# coding=utf-8


from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from keyboards.reply_keyboards.menu import *
from keyboards.reply_keyboards.back_admin import *
from services.project.cities_controller import CitiesController


cities_controller = CitiesController()


class CitiesAddState(StatesGroup):
    waiting_for_city = State()


class CitiesDelState(StatesGroup):
    waiting_for_city = State()
    waiting_for_accept = State()


async def add_city(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")
    await message.edit_text("<b>Добавление города</b>")

    await message.answer("🏙 <b>Введите имя города</b>\n\n"
                         "<code>Для отмены добавления города, нажмите "
                         "на кнопку</code> <b>Отменить</b>", reply_markup=back_admin_keyboard)

    await CitiesAddState.waiting_for_city.set()


async def add_city_choosing(message: types.Message, state: FSMContext):
    city_name = message.text

    if city_name != "Отменить":
        await cities_controller.add_city(city_name)
        await message.answer("✅ <b>Добавлен новый город</b>")

        await state.finish()
    else:
        await message.answer("⚠️ <b>Добавление города отменено</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


async def del_city(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")

    cities = await cities_controller.get_cities()

    if len(cities) != 0:
        cities_info_blocks = []

        for city in cities:
            city_id = city[0]
            city_name = city[1]

            cities_info_blocks.append(
                f"<b>id:</b> <code>{city_id}</code>\n"
                f"<b>Имя:</b> <code>{city_name}</code>"
            )

        cities_message = '\n➖➖➖➖\n'.join(cities_info_blocks)

        await message.answer("<b>Список загружен</b>", reply_markup=menu_keyboard)
        await message.edit_text(cities_message)

    await message.answer("🏙 <b>Введите id города, который необходимо удалить</b>\n\n"
                         "<code>Для отмены удаления города, нажмите "
                         "нв кнопку</code> <b>Отменить</b>", reply_markup=menu_keyboard)

    await CitiesDelState.waiting_for_city.set()


async def del_city_choosing(message: types.Message, state: FSMContext):
    city_id = message.text

    if city_id != "Отменить":
        try:
            int(city_id)
        except:
            await message.answer("⚠️ <b>id города должен быть числом</b>")
            return

        does_city_exist = await cities_controller.does_city_exist(city_id)

        if does_city_exist:
            accept_keyboard = types.InlineKeyboardMarkup()

            no_button = types.InlineKeyboardButton("Нет", callback_data="cities_delete_no")
            yes_button = types.InlineKeyboardButton("Да", callback_data="cities_delete_yes")

            accept_keyboard.add(yes_button, no_button)

            await message.answer(f"❗️ <b>Вы точно хотите удалить город id</b> "
                                 f"<code>{city_id}</code>?", reply_markup=accept_keyboard)
            await redis_helper.redis_set("city_id", city_id)

            await CitiesDelState.waiting_for_accept.set()
        else:
            await message.answer("⚠️ <b>Такого города не существует</b>\n\n"
                                 "<code>Воспользуйтесь уже загруженным списком городов</code>")
            return
    else:
        await message.answer("⚠️ <b>Удаление города отменено</b>", reply_markup=menu_keyboard)
        await state.finish()


async def del_city_accepting(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    accept = callback_query.data.replace("cities_delete_", '')

    await callback_query.answer("Загрузка...")

    if accept == "yes":
        city_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("city_id")
        ))
        await cities_controller.del_city(city_id)

        await message.edit_text("✅ <b>Город удален</b>")

        await state.finish()
    elif accept == "no":
        await message.edit_text("⚠ <b>Удаление города отменено</b>")
        await message.answer("<b>Открытие меню</b>", reply_markup=menu_keyboard)

        await state.finish()

    await state.finish()


async def get_cities(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка городов...")

    cities = await cities_controller.get_cities()

    if len(cities) != 0:
        cities_info_blocks = []

        for city in cities:
            city_id = city[0]
            city_name = city[1]

            cities_info_blocks.append(
                f"<b>id:</b> <code>{city_id}</code>\n"
                f"<b>Имя:</b> <code>{city_name}</code>"
            )

        cities_message = '\n➖➖➖➖\n'.join(cities_info_blocks)

        await message.answer("<b>Список загружен</b>", reply_markup=menu_keyboard)
        await message.edit_text(cities_message)
    else:
        await message.edit_text("<b>Просмотр городов</b>")
        await message.answer("⚠️ <b>Городов пока что нет</b>", reply_markup=menu_keyboard)


def register_handlers_admin_cities(dp: Dispatcher):
    dp.register_callback_query_handler(
        add_city,
        lambda callback_query: callback_query.data and callback_query.data == "admin_cities_add",
        state=None
    )
    dp.register_message_handler(
        add_city_choosing,
        content_types=['text'], state=CitiesAddState.waiting_for_city
    )
    dp.register_callback_query_handler(
        del_city,
        lambda callback_query: callback_query.data and callback_query.data == "admin_cities_del",
        state=None
    )
    dp.register_message_handler(
        del_city_choosing,
        content_types=['text'], state=CitiesDelState.waiting_for_city
    )
    dp.register_callback_query_handler(
        del_city_accepting,
        lambda callback_query: callback_query.data and callback_query.data.startswith("cities_delete_"),
        state=CitiesDelState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        get_cities,
        lambda callback_query: callback_query.data and callback_query.data == "admin_cities_get"
    )
