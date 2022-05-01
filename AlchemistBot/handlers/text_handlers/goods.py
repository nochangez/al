# coding=utf-8


from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from services.payment.qiwi import Payments
from keyboards.reply_keyboards.back import *
from keyboards.reply_keyboards.menu import *
from services.project.user_controller import UserController
from services.project.goods_controller import GoodsController

payments = Payments()
user_controller = UserController()
goods_controller = GoodsController()


class OrderGoodState(StatesGroup):
    waiting_for_good_name = State()


async def goods(message: types.Message):
    user_id = message.from_user.id
    is_user = await user_controller.is_user(user_id)

    if is_user:
        all_goods = await goods_controller.get_goods()
        city = await user_controller.get_user_info(user_id)
        city = city[2]

        if len(all_goods) != 0:
            goods_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            for good in all_goods:
                good_name = str(good[1])
                goods_keyboard.add(f"🎁 {good_name}")

            goods_keyboard.add(back_button)

            await message.answer(f"🏠 <b>Город</b>: {city}\n"
                                 "➖➖➖➖\n"
                                 "<b>Выберите товар</b>:", reply_markup=goods_keyboard)

            await OrderGoodState.waiting_for_good_name.set()
        else:
            no_goods_message = "⚠️ <b>Товаров пока что нет!</b>\n\n"
            await message.answer(no_goods_message)
    else:
        not_user_message = f"⚠️ <b>{message.from_user.first_name}</b>, " \
                           f"Вы пока что <u>не зарегистрированы</u>!\n\n" \
                           f"<code>Пройти регистрацию можно по команде</code> /start"
        await message.answer(not_user_message)


async def good_name_choosing(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    good_name = message.text.replace("🎁 ", '')
    does_good_exist = await goods_controller.does_good_exist_name(good_name)

    if does_good_exist and good_name != "🏡 Вернуться в меню":
        user_info = await user_controller.get_user_info(user_id)
        balance = float(user_info[-1])

        good_info = await goods_controller.get_good_by_name(good_name)
        good_price = float(good_info[-1])

        good_info_message = f"🪅 <b>Информация о товаре:</b>\n\n" \
                            f"🎁 <b>Имя:</b> <code>{good_name}</code>\n" \
                            f"💸 <b>Цена:</b> <code>{good_price}</code> руб."
        await message.answer(good_info_message, reply_markup=back_keyboard)

        if balance < good_price:
            new_balance = float(balance - good_price)
            need_money = float(good_price - balance)

            no_money_message = "⚠️ <b>Недостаточно средств!</b>\n\n" \
                               f"💸 <b>Цена:</b> <code>{good_price}</code> руб.\n" \
                               f"💰 <b>Баланс:</b> <code>{balance}</code> руб.\n" \
                               f"🧮 <b>Нужно:</b> <code>{need_money}</code> руб.\n\n" \
                               f"🪙 <b>Итого к оплате:</b> <code>{need_money}</code> руб.\n" \
                               f"⏳ <b>Счет закроется через:</b> <code>5 мин.</code>\n\n" \
                               f"<code>Нажмите на кнопку</code> <b>✅ Проверить оплату</b> <code>после перевода " \
                               f"средств. Сразу после покупки Вы получите местоположение товара</code>\n\n" \
                               "<code>Вы можете купить этот товар прямо сейчас</code> 👇"

            bill = await payments.create_payment(amount=need_money)

            bill_id = bill.get('bill_id')
            pay_url = bill.get('pay_url')

            buy_keyboard = types.InlineKeyboardMarkup()

            payment_url_button = types.InlineKeyboardButton("💳 Оплатить", url=pay_url)
            check_payment_button = types.InlineKeyboardButton(
                "✅ Проверить оплату",
                callback_data=f"buy_check_payment_{bill_id}"
            )
            buy_keyboard.add(payment_url_button).add(check_payment_button)

            await message.answer(no_money_message, reply_markup=buy_keyboard)

            await redis_helper.redis_set("good_price", need_money)
        else:
            new_balance = float(balance - good_price)
            await redis_helper.redis_set("new_balance", new_balance)

            payment_created_message = f"✅ <b>Покупка ожидает подтверждения!</b>\n\n" \
                                      f"💸 <b>Цена:</b> <code>{good_price}</code> руб.\n" \
                                      f"💰 <b>Баланс:</b> <code>{balance}</code> руб.\n" \
                                      f"🧮 <b>Останется:</b> <code>{new_balance}</code> руб.\n\n" \
                                      f"🪙 <b>Итого к оплате:</b> <code>{good_price}</code> руб.\n\n" \
                                      f"<code>Вы подтверждаете платеж?</code>" \

            accept_keyboard = types.InlineKeyboardMarkup()

            no_button = types.InlineKeyboardButton("Нет", callback_data="accept_pay_no")
            yes_button = types.InlineKeyboardButton("Да", callback_data="accept_pay_yes")

            accept_keyboard.add(yes_button, no_button)

            await message.answer(payment_created_message, reply_markup=accept_keyboard)

        await state.finish()
    else:
        if good_name != "🏡 Вернуться в меню":
            no_goods_message = f"⚠ <b>Товар не найден!</b>\n\n" \
                               f"Товар с именем \"<code>{good_name}</code>\" " \
                               f"не обнаружен в списке доступных товаров.\n\n" \
                               f"<b>Подсказка:</b>\n<code>Для большего удобства используйте " \
                               f"клавиатуру с уже подготовленными, доступными и существующими товарами</code>"
            await message.answer(no_goods_message)
            return
        else:
            await state.finish()
            await message.answer("<b>Выбор товара отменен!</b>", reply_markup=menu_keyboard)


async def accept_payment(callback_query: types.CallbackQuery):
    message = callback_query.message
    user_accept = callback_query.data.replace("accept_pay_", '')

    await callback_query.answer("Подтверждение платежа...")

    if user_accept == "yes":
        new_balance = float(await redis_helper.decode_bytes(
            await redis_helper.redis_get("new_balance")
        ))

        await user_controller.change_balance(callback_query.from_user.id, new_balance)
        await user_controller.add_purchase(callback_query.from_user.id)

        await message.edit_text("✅ <b>Товар успешно оплачен</b>\n\n"
                                "<code>За товаром обращайтесь сюда</code> @alhimik_tg")
    elif user_accept == "no":
        await message.edit_text("⚠ <b>Платеж отклонен!</b>")


def register_handlers_goods(dp: Dispatcher):
    dp.register_message_handler(goods, lambda message: message.text and message.text == "🪨 Товар", state=None)
    dp.register_message_handler(
        good_name_choosing,
        lambda message: message.text,
        state=OrderGoodState.waiting_for_good_name
    )
    dp.register_callback_query_handler(
        accept_payment,
        lambda callback_query: callback_query.data and callback_query.data.startswith("accept_pay")
    )
