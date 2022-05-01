# coding=utf-8


from datetime import datetime

from aiogram import Dispatcher, types
from pyqiwip2p.p2p_types.errors import QiwiError

from services.payment.qiwi import Payments
from keyboards.reply_keyboards.menu import *
from data.config import redis_helper, admins, bot
from services.project.user_controller import UserController
from services.payment.payments_controller import PaymentsController


payments = Payments()
user_controller = UserController()
payments_controller = PaymentsController()


async def check_top_up_balance(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Проверка платежа...")

    try:
        bill_id = callback_query.data.replace("check_payment_", '')
        is_paid = await payments.get_payment_status(bill_id)

        if is_paid:
            amount = float(await redis_helper.decode_bytes(
                await redis_helper.redis_get('top_up_amount')
            ))

            old_balance = float((await user_controller.get_user_info(callback_query.from_user.id))[-1])
            new_balance = amount + old_balance

            await user_controller.change_balance(callback_query.from_user.id, new_balance)
            await payments_controller.add_payment(callback_query.from_user.id, amount)

            await message.edit_text("✅ <b>Счет пополнен</b>")
            await message.answer(f"<b>Пополнение:</b> <code>{amount}</code> ₽\n"
                                 f"<b>Старый баланс:</b> <code>{old_balance}</code> ₽\n"
                                 f"<b>Новый баланс:</b> <code>{new_balance}</code> ₽",
                                 reply_markup=menu_keyboard)

            date = (datetime.now()).strftime("%d.%m.%Y %H:%M:%S")

            for admin in admins:
                new_payment_message = "📥 <b>Новое пополнение!</b>\n\n" \
                                      f"<b>Покупатель:</b> <a " \
                                      f"href=\"tg://user?id={callback_query.from_user.id}\">" \
                                      f"{callback_query.from_user.first_name}</a>\n\n" \
                                      f"<b>Статус:</b> ✅\n" \
                                      f"<b>Сумма:</b> {amount} ₽\n" \
                                      f"<b>Дата:</b> {date}"
                try:
                    print(admin)
                    await bot.send_message(admin, new_payment_message)
                except Exception as error:
                    print(error)
        else:
            await message.answer("❌ <b>Вы не оплатили счет!</b>")
    except QiwiError as error:
        error = str(error.error_code)
        if error == "api.invoice.not.found":
            await message.edit_text("⚠ <b>Счет не найден!</b>")


async def check_top_up_buying(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Проверка платежа...")

    try:
        bill_id = callback_query.data.replace("buy_check_payment_", '')
        is_paid = await payments.get_payment_status(bill_id)

        if is_paid:
            amount = float(await redis_helper.decode_bytes(
                await redis_helper.redis_get('good_price')
            ))

            balance = float((await user_controller.get_user_info(callback_query.from_user.id))[-1])
            new_balance = (balance - amount) if balance > 0.0 else 0.0

            await user_controller.change_balance(callback_query.from_user.id, new_balance)
            await payments_controller.add_payment(callback_query.from_user.id, amount)
            await user_controller.add_purchase(callback_query.from_user.id)

            await message.edit_text("✅ <b>Покупка совершена</b>\n\n"
                                    "<code>За товаром обращайтесь сюда </code> @alhimik_tg")
            await message.answer(f"<b>Сумма:</b> <code>{amount}</code> ₽\n"
                                 f"<b>Старый баланс:</b> <code>{balance}</code> ₽\n"
                                 f"<b>Новый баланс:</b> <code>{new_balance}</code> ₽",
                                 reply_markup=menu_keyboard)

            date = (datetime.now()).strftime("%d.%m.%Y %H:%M:%S")

            for admin in admins:
                new_payment_message = "📥 <b>Новое пополнение!</b>\n\n" \
                                      f"<b>Покупатель:</b> <a " \
                                      f"href=\"tg://user?id={callback_query.from_user.id}\">" \
                                      f"{callback_query.from_user.first_name}</a>\n\n" \
                                      f"<b>Статус:</b> ✅\n" \
                                      f"<b>Сумма:</b> {amount} ₽\n" \
                                      f"<b>Дата:</b> {date}"
                try:
                    print(admin)
                    await bot.send_message(admin, new_payment_message)
                except Exception as error:
                    print(error)
                    continue
        else:
            await message.answer("❌ <b>Вы не оплатили счет!</b>")
    except QiwiError as error:
        error = str(error.error_code)
        if error == "api.invoice.not.found":
            await message.edit_text("⚠ <b>Счет не найден!</b>")


def register_handlers_check_payment(dp: Dispatcher):
    dp.register_callback_query_handler(
        check_top_up_balance,
        lambda callback_query: callback_query.data and callback_query.data.startswith("check_payment_")
    )
    dp.register_callback_query_handler(
        check_top_up_buying,
        lambda callback_query: callback_query.data and callback_query.data.startswith("buy_check_payment_")
    )
