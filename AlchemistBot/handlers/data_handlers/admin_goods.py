# coding=utf-8


from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from keyboards.reply_keyboards.menu import *
from keyboards.reply_keyboards.accept import *
from services.project.goods_controller import GoodsController
from keyboards.reply_keyboards.back_admin import back_admin_keyboard


goods_controller = GoodsController()


class AddGoodState(StatesGroup):
    waiting_for_good = State()
    waiting_for_price = State()


class DelGoodState(StatesGroup):
    waiting_for_good = State()


class ChangeGoodState(StatesGroup):
    waiting_for_good = State()


class ChangeGoodNameState(StatesGroup):
    waiting_for_name = State()
    waiting_for_accept = State()


class ChangeGoodPriceState(StatesGroup):
    waiting_for_price = State()
    waiting_for_accept = State()


async def add_good(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()
    await message.edit_text("<b>Добавление товара</b>")
    await message.answer("➕ Введите <b>имя</b> товара", reply_markup=back_admin_keyboard)

    await AddGoodState.waiting_for_good.set()


async def add_good_choose_name(message: types.Message, state: FSMContext):
    good_name = message.text

    if str(good_name) != "Отменить":
        await redis_helper.redis_set('good_name', good_name)

        await message.answer("✅ <b>Имя сохранено</b>")
        await message.answer("➕ Введите <b>сумму</b> товара числом\n\n"
                             "<code>Например: 7000 или 3000.45</code>")

        await AddGoodState.next()
    else:
        await message.answer("✅ <b>Добавление товара отменено</b>", reply_markup=menu_keyboard)
        await state.finish()


async def add_good_choose_price(message: types.Message, state: FSMContext):
    price = message.text

    if str(price) != "Отменить":
        try:
            float(price)
        except:
            await message.answer("❗️ Сумма должна быть числом!\n"
                                 "Попробуйте снова\n\n<code>Для отмены удаления товара "
                                 "нажмите на кнопку \"Отменить\"</code>")
            return

        price = float(price)

        await redis_helper.redis_set('price', price)
        await message.answer("✅ <b>Сумма сохранена</b>")

        good_name = await redis_helper.decode_bytes(
            await redis_helper.redis_get('good_name')
        )
        await goods_controller.add_good(good_name=good_name, price=price)

        good_id = await goods_controller.get_good_by_name(good_name)
        good_id = good_id[0]

        await message.answer("✅ Добавлен новый товар!\n\n"
                             f"<b>id</b>: <code>{good_id}</code>\n"
                             f"<b>Имя</b>: <code>{good_name}</code>\n"
                             f"<b>Цена</b>: <code>{price}</code>", reply_markup=menu_keyboard)
    else:
        await message.answer("✅ <b>Добавление товара отменено</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


async def del_good(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    goods = await goods_controller.get_goods()

    if len(goods) != 0:
        good_info_blocks = []

        for good in goods:
            price = float(good[2])
            good_id = int(good[0])
            good_name = str(good[1])

            good_info_blocks.append(
                f"<b>id</b>: <code>{good_id}</code>\n"
                f"<b>Имя</b>: <code>{good_name}</code>\n"
                f"<b>Цена</b>: <code>{price} руб.</code>"
            )

        goods_message = '\n➖➖➖➖\n'.join(good_info_blocks)
        await message.edit_text(goods_message)

        await message.answer("<b>Список доступных товаров загружен</b> ☝️", reply_markup=back_admin_keyboard)
        await message.answer("📮 <b>Введите номер (id) товара, который необходимо "
                             "удалить числом</b>\n\n"
                             "<code>Например: 1 или 9</code>")

        await DelGoodState.waiting_for_good.set()
    else:
        await message.edit_text("<b>Удаление товара</b>")
        no_goods_message = "⚠️ <b>Товаров пока что нет!</b>\n\n" \
                           "<code>Управление товарами осуществляется в " \
                           "админ панели, вызвать ее можно нажав сюда</code> /admin"
        await message.answer(no_goods_message, reply_markup=menu_keyboard)


async def del_good_choosing_id(message: types.Message, state: FSMContext):
    good_id = message.text

    if str(good_id) != "Отменить":
        try:
            int(good_id)
        except:
            await message.answer("❗ Id товара должен быть числом!\n"
                                 "Попробуйте снова\n\n<code>Для отмены удаления товара "
                                 "нажмите на кнопку \"Отменить\"</code>")
            return

        does_good_exist = await goods_controller.does_good_exist_id(good_id)

        if does_good_exist:
            good_id = int(good_id)
            await goods_controller.del_good(good_id)

            await message.answer("✅ <b>Товар успешно удален!</b>", reply_markup=menu_keyboard)

            await state.finish()
        else:
            await message.answer("⚠ <b>Товар не найден!</b>️\n\n"
                                 f"Товар с id <code>{good_id}</code> не найден, повторите попытку.\n\n"
                                 f"<code>Все доступные товары были загружены ранее, выберите id товара "
                                 f"из того списка</code>")
            return
    else:
        await message.answer("✅ <b>Удаление товара отменено</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


async def change_good(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    goods = await goods_controller.get_goods()

    if len(goods) != 0:
        good_info_blocks = []

        for good in goods:
            price = float(good[2])
            good_id = int(good[0])
            good_name = str(good[1])

            good_info_blocks.append(
                f"<b>id</b>: <code>{good_id}</code>\n"
                f"<b>Имя</b>: <code>{good_name}</code>\n"
                f"<b>Цена</b>: <code>{price} руб.</code>"
            )

        goods_message = '\n➖➖➖➖\n'.join(good_info_blocks)
        await message.edit_text(goods_message)

        await message.answer("<b>Список доступных товаров загружен</b> ☝️", reply_markup=back_admin_keyboard)
        await message.answer("🖊 <b>Введите номер (id) товара, который необходимо "
                             "изменить числом</b>\n\n"
                             "<code>Например: 1 или 9</code>")

        await ChangeGoodState.waiting_for_good.set()
    else:
        await message.edit_text("<b>Изменение товара</b>")
        no_goods_message = "⚠️ <b>Товаров пока что нет!</b>\n\n" \
                           "<code>Управление товарами осуществляется в " \
                           "админ панели, вызвать ее можно нажав сюда</code> /admin"
        await message.answer(no_goods_message, reply_markup=menu_keyboard)


async def change_good_choosing_id(message: types.Message, state: FSMContext):
    good_id = message.text

    if str(good_id) != "Отменить":
        try:
            int(good_id)
        except:
            await message.answer("❗ Id товара должен быть числом!\n"
                                 "Попробуйте снова\n\n<code>Для отмены изменения товара "
                                 "нажмите на кнопку \"Отменить\"</code>")
            return

        does_good_exist = await goods_controller.does_good_exist_id(good_id)

        if does_good_exist:
            good_id = int(good_id)
            await redis_helper.redis_set("good_id", good_id)

            change_keyboard = types.InlineKeyboardMarkup()

            change_name_button = types.InlineKeyboardButton("Изменить имя", callback_data="goods_change_name")
            change_price_button = types.InlineKeyboardButton("Изменить цену", callback_data="goods_change_price")

            change_keyboard.add(change_name_button).add(change_price_button)

            await message.answer("✍️ <b>Выберите, что именно Вы хотите изменить:</b>", reply_markup=change_keyboard)

            await state.finish()
        else:
            await message.answer("⚠ <b>Товар не найден!</b>️\n\n"
                                 f"Товар с id <code>{good_id}</code> не найден, повторите попытку.\n\n"
                                 f"<code>Все доступные товары были загружены ранее, выберите id товара "
                                 f"из того списка</code>")
            return
    else:
        await message.answer("✅ <b>Изменение товара отменено!</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


async def change_good_name(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    await message.edit_text("<b>Изменение имени товара</b>")
    await message.answer("➕ Введите <b>новое имя</b> товара", reply_markup=back_admin_keyboard)

    await ChangeGoodNameState.waiting_for_name.set()


async def change_good_name_choosing(message: types.Message, state: FSMContext):
    new_good_name = message.text

    if new_good_name != "Отменить":
        good_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("good_id")
        ))

        does_good_exist = await goods_controller.does_good_exist_id(good_id)

        if does_good_exist:
            good_info = await goods_controller.get_good_by_id(good_id)
            old_good_name = good_info[1]

            change_good_name_message = f"⚠ <b>Подтвердите действие</b>\n\n" \
                                       f"👨‍🦳 <b>Старое имя</b>: <code>{old_good_name}</code>\n" \
                                       f"⚜️ <b>Новое имя</b>: <code>{new_good_name}</code>\n\n" \
                                       "<code>Да - подтверждаю\n" \
                                       "Нет - отклоняю</code>"
            await message.answer(change_good_name_message, reply_markup=accept_keyboard)
            await redis_helper.redis_set("new_good_name", new_good_name)

            await ChangeGoodNameState.next()
        else:
            await message.answer("⚠ <b>Товар не найден!</b>️\n\n"
                                 f"Товар с id <code>{good_id}</code> не найден, повторите попытку.\n\n"
                                 f"<code>Все доступные товары были загружены ранее, выберите id товара "
                                 f"из того списка</code>")
            return
    else:
        await message.answer("✅ <b>Изменение имени товара отменено!</b>", reply_markup=menu_keyboard)
        await state.finish()


async def change_good_name_accept(message: types.Message, state: FSMContext):
    accept_answer = message.text

    if accept_answer.lower() in ('да', 'нет'):
        if accept_answer.lower() == "да":
            good_id = int(await redis_helper.decode_bytes(
                await redis_helper.redis_get("good_id")
            ))
            new_good_name = str(await redis_helper.decode_bytes(
                await redis_helper.redis_get("new_good_name")
            ))

            await goods_controller.change_good_name(good_id, new_good_name)
            await message.answer("✅ <b>Имя товара успешно изменено!</b>", reply_markup=menu_keyboard)

            await state.finish()
        elif accept_answer.lower() == "нет":
            await message.answer("✅ <b>Изменение имени товара отменено!</b>", reply_markup=menu_keyboard)
            await state.finish()
    else:
        await message.answer("<code>Да</code> <b>или</b> <code>Нет</code>")
        return

    await state.finish()


async def change_good_price(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    await message.edit_text("<b>Изменение цены товара</b>")
    await message.answer("➕ Введите <b>новую цену</b> товара", reply_markup=back_admin_keyboard)

    await ChangeGoodPriceState.waiting_for_price.set()


async def change_good_price_choosing(message: types.Message, state: FSMContext):
    new_good_price = message.text

    if new_good_price != "Отменить":
        try:
            float(new_good_price)
        except:
            await message.answer("❗ <b>Сумма должна быть числом!</b>\n\n"
                                 "Попробуйте снова.\n\n<code>Для отмены изменения "
                                 "цены товара нажмите на кнопку \"Отменить\"</code>")
            return

        good_id = int(await redis_helper.decode_bytes(
            await redis_helper.redis_get("good_id")
        ))

        does_good_exist = await goods_controller.does_good_exist_id(good_id)

        if does_good_exist:
            good_info = await goods_controller.get_good_by_id(good_id)
            old_good_price = good_info[-1]

            change_good_name_message = f"⚠ <b>Подтвердите действие</b>\n\n" \
                                       f"🪙 <b>Старая цена</b>: <code>{old_good_price}</code> руб.\n" \
                                       f"💵️ <b>Новая цена</b>: <code>{new_good_price}</code> руб.\n\n" \
                                       "<code>Да - подтверждаю\n" \
                                       "Нет - отклоняю</code>"
            await message.answer(change_good_name_message, reply_markup=accept_keyboard)
            await redis_helper.redis_set("new_good_price", new_good_price)

            await ChangeGoodPriceState.next()
        else:
            await message.answer("⚠ <b>Товар не найден!</b>️\n\n"
                                 f"Товар с id <code>{good_id}</code> не найден, повторите попытку.\n\n"
                                 f"<code>Все доступные товары были загружены ранее, выберите id товара "
                                 f"из того списка</code>")
            return
    else:
        await message.answer("✅ <b>Изменение цены товара отменено!</b>", reply_markup=menu_keyboard)
        await state.finish()


async def change_good_price_choosing_accept(message: types.Message, state: FSMContext):
    accept_answer = message.text

    if accept_answer.lower() in ('да', 'нет'):
        if accept_answer.lower() == "да":
            good_id = int(await redis_helper.decode_bytes(
                await redis_helper.redis_get("good_id")
            ))
            new_good_price = float(await redis_helper.decode_bytes(
                await redis_helper.redis_get("new_good_price")
            ))

            await goods_controller.change_good_price(good_id, new_good_price)
            await message.answer("✅ <b>Цена товара успешно изменена!</b>", reply_markup=menu_keyboard)

            await state.finish()
        elif accept_answer.lower() == "нет":
            await message.answer("✅ <b>Изменение цены товара отменено!</b>", reply_markup=menu_keyboard)
            await state.finish()
    else:
        await message.answer("<code>Да</code> <b>или</b> <code>Нет</code>")
        return

    await state.finish()


async def show_goods(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    goods = await goods_controller.get_goods()

    if len(goods) != 0:
        good_info_blocks = []

        for good in goods:
            price = float(good[2])
            good_id = int(good[0])
            good_name = str(good[1])

            good_info_blocks.append(
                f"<b>id</b>: <code>{good_id}</code>\n"
                f"<b>Имя</b>: <code>{good_name}</code>\n"
                f"<b>Цена</b>: <code>{price} руб.</code>"
            )

        goods_message = '\n➖➖➖➖\n'.join(good_info_blocks)

        await message.answer("<b>Список загружен</b>", reply_markup=menu_keyboard)
        await message.edit_text(goods_message)
    else:
        no_goods_message = "⚠️ <b>Товаров пока что нет!</b>\n\n" \
                           "<code>Управление товарами осуществляется в " \
                           "админ панели, вызвать ее можно нажав сюда</code> /admin"
        await message.edit_text(no_goods_message)


def register_handlers_admin_goods(dp: Dispatcher):
    dp.register_callback_query_handler(
        add_good,
        lambda callback_query: callback_query.data and callback_query.data == "admin_goods_add",
        state=None
    )
    dp.register_message_handler(add_good_choose_name, content_types=['text'], state=AddGoodState.waiting_for_good)
    dp.register_message_handler(add_good_choose_price, content_types=['text'], state=AddGoodState.waiting_for_price)
    dp.register_callback_query_handler(
        del_good,
        lambda callback_query: callback_query.data and callback_query.data == "admin_goods_del",
        state=None
    )
    dp.register_message_handler(del_good_choosing_id, content_types=['text'], state=DelGoodState.waiting_for_good)
    dp.register_callback_query_handler(
        change_good,
        lambda callback_query: callback_query.data and callback_query.data == "admin_goods_change",
        state=None
    )
    dp.register_message_handler(change_good_choosing_id, content_types=['text'], state=ChangeGoodState.waiting_for_good)
    dp.register_callback_query_handler(
        change_good_name,
        lambda callback_query: callback_query.data and callback_query.data == "goods_change_name",
        state=None
    )
    dp.register_message_handler(
        change_good_name_choosing,
        content_types=['text'], state=ChangeGoodNameState.waiting_for_name
    )
    dp.register_message_handler(
        change_good_name_accept,
        content_types=['text'], state=ChangeGoodNameState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        change_good_price,
        lambda callback_query: callback_query.data and callback_query.data == "goods_change_price",
        state=None
    )
    dp.register_message_handler(
        change_good_price_choosing,
        content_types=['text'], state=ChangeGoodPriceState.waiting_for_price
    )
    dp.register_message_handler(
        change_good_price_choosing_accept,
        content_types=['text'], state=ChangeGoodPriceState.waiting_for_accept
    )
    dp.register_callback_query_handler(
        show_goods,
        lambda callback_query: callback_query.data and callback_query.data == "admin_goods_show"
    )
