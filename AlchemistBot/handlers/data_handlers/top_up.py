# coding=utf-8


from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data.config import redis_helper
from services.payment.qiwi import Payments
from keyboards.reply_keyboards.back import *
from keyboards.reply_keyboards.menu import *


payments = Payments()


class TopUpState(StatesGroup):
    waiting_for_amount = State()


ready_amounts_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
ready_amounts_keyboard.add("500", "1000").add("1500", "3000").add("5500", "10000").add(back_button)


async def top_up(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer()

    await message.edit_text("📥 <b>Пополнение баланса</b>")
    await message.answer("💵 <b>Введите сумму числом (в рублях), на которую вы хотели бы "
                         "пополить свой баланс</b>\n\n"
                         "<code>Например: 5000 или 2500.40</code>\n\n"
                         "<b>Вы также можете воспользоваться "
                         "уже подготовленными суммами для пополнения (их можно найти "
                         "на клавиатуре ниже)</b>\n\n"
                         "<code>Чтобы отменить пополнение, нажмите на кнопку</code> "
                         "<b>🏡 Вернуться в меню</b>", reply_markup=ready_amounts_keyboard)

    await TopUpState.waiting_for_amount.set()


async def top_up_choosing(message: types.Message, state: FSMContext):
    amount = message.text

    if amount != "🏡 Вернуться в меню":
        try:
            float(amount)
        except:
            await message.answer("⚠ <b>Пополняемая сумма должна быть числом!</b>\n\n"
                                 "<code>Вы также можете воспользоваться уже подготовленными "
                                 "для оплаты суммами, их можно найти на клавиатуре ниже</code>",
                                 reply_markup=ready_amounts_keyboard)
            return

        bill = await payments.create_payment(amount=amount)

        bill_id = bill.get('bill_id')
        pay_url = bill.get('pay_url')

        buy_keyboard = types.InlineKeyboardMarkup()

        payment_url_button = types.InlineKeyboardButton("💳 Оплатить", url=pay_url)
        check_payment_button = types.InlineKeyboardButton(
            "✅ Проверить оплату",
            callback_data=f"check_payment_{bill_id}"
        )
        buy_keyboard.add(payment_url_button).add(check_payment_button)

        await redis_helper.redis_set("top_up_amount", amount)

        await message.answer("📤 <b>Счет успешно создан!</b>", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"💰 <b>К оплате:</b> <code>{amount}</code> руб.\n"
                             f"⏳ <b>Счет закроется через:</b> <code>5</code> мин.\n\n"
                             f"<code>После оплаты нажмите на кнопку</code>\n"
                             f"<b>✅ Проверить оплату</b>", reply_markup=buy_keyboard)

        await state.finish()
    else:
        await message.answer("⚠️ <b>Пополнение баланса отменено</b>", reply_markup=menu_keyboard)
        await state.finish()

    await state.finish()


def register_handlers_top_up(dp: Dispatcher):
    dp.register_callback_query_handler(
        top_up,
        lambda callback_query: callback_query.data and callback_query.data == "top_up_balance",
        state=None
    )
    dp.register_message_handler(top_up_choosing, content_types=['text'], state=TopUpState.waiting_for_amount)
