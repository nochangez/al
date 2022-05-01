# coding=utf-8


from datetime import datetime
from os import remove, listdir

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from services.help.additions import *
from services.help.decorators import *
from keyboards.reply_keyboards.menu import *
from keyboards.inline_keyboards.admin import *
from data.config import path_to_config_files, bot
from keyboards.reply_keyboards.back_admin import *
from services.help.write_report import write_in_file
from services.project.payments_controller import PaymentsController


payments_controller = PaymentsController()


class GetPaymentsDateState(StatesGroup):
    waiting_for_date = State()


class GetPaymentPeriodState(StatesGroup):
    waiting_for_period = State()


async def get_payments(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загузка...")
    await message.edit_text("<b>Просмотр всех платежей</b>")

    payments = await payments_controller.get_payments()

    if len(payments) != 0:
        loading_start = await message.answer("<b>Началась выгрузка платежей...</b>")

        payments_report_start_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        remove(f"{path_to_config_files}Отчет - платежи.txt") \
            if "Отчет - платежи.txt" in listdir(f"{path_to_config_files}") else None

        payments_report_file = open(f"{path_to_config_files}Отчет - платежи.txt", 'w+', encoding='utf-8')
        payments_report_file.close()

        total_money = 0.0

        for payment in payments:
            payment_id = payment[0]
            customer_id = payment[1]
            payment_value = float(payment[2])
            payment_date = payment[3].strftime("%d.%m.%Y %H:%M:%S")

            total_money += payment_value

            with open(f"{path_to_config_files}Отчет - платежи.txt", 'a+', encoding='utf-8') as payments_report_file:
                payment_report_message = f"id Платежа: {payment_id}\n" \
                                         f"Статус операции: ✅\n" \
                                         f"id Покупателя: {customer_id}\n" \
                                         f"Сумма платежа: {payment_value} RUB 🇷🇺\n" \
                                         f"Дата операции: {payment_date}\n\n" \
                                         f"#########################################\n\n"
                payments_report_file.write(payment_report_message)

                total_report_message = "#########################################\n" \
                                       "###################TOTAL#################\n" \
                                       "#########################################\n\n" \
                                       f"Итог за все время: {total_money} RUB 🇷🇺"

        with open(f"{path_to_config_files}Отчет - платежи.txt", 'a+', encoding='utf-8') as payments_report_file:
            payments_report_file.write(total_report_message)

        payments_report_end_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=loading_start.message_id,
            text="<b>Выгрузка платежей закончена</b>",
        )

        await message.answer("<b>Открываю панель администратора</b>", reply_markup=admin_keyboard)

        await bot.send_document(
            callback_query.from_user.id,
            open(f"{path_to_config_files}Отчет - платежи.txt"),
            caption=f"✅ <b>Сбор информации о платежах закончен</b>\n\n"
                    f"<b>Начало сбора:</b> {payments_report_start_time}\n"
                    f"<b>Конец сбора:</b> {payments_report_end_time}\n\n"
                    f"<b>Итог:</b> {total_money} RUB 🇷🇺\n\n"
                    f"<code>Прикрепляю отчет по платежам за все время</code>"
        )
    else:
        await message.answer("⚠️ <b>Платежных операций пока что не обнаружено</b>", reply_markup=admin_keyboard)


async def get_payment_date(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Заргузка...")

    await message.edit_text("<b>Просмотр доходов по дате</b>")
    await message.answer("📅 <b>Введите дату, доход которой Вас интересует</b>\n\n"
                         "<code>Дата должна быть вида ДД.ММ.ГГГГ</code>\n\n"
                         "<code>Для отмены просмотра выписки платежей нажмите на "
                         "кнопку \"Отменить\"</code>", reply_markup=back_admin_keyboard)

    await GetPaymentsDateState.waiting_for_date.set()


async def get_payment_date_choosing(message: types.Message, state: FSMContext):
    date = message.text

    if date != "Отменить":
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            await message.answer("⚠️ <b>Дата должна быть полностью идентична шаблону</b> "
                                 "<code>ДД.ММ.ГГГГ</code>")
            return

        searching_date = datetime.strptime(date, "%d.%m.%Y")
        searching_date = searching_date.strftime("%Y-%m-%d")

        payments = await payments_controller.get_payments_by_date(searching_date)

        if len(payments) != 0:
            loading_start = await message.answer("<b>Началась выгрузка платежей...</b>")

            payments_report_start_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

            remove(f"{path_to_config_files}Отчет - платежи {date}.txt") \
                if f"Отчет - платежи {date}.txt" in listdir(f"{path_to_config_files}") else None

            payments_report_file = open(f"{path_to_config_files}Отчет - платежи {date}.txt", 'w+', encoding='utf-8')
            payments_report_file.close()

            total_money = 0.0

            for payment in payments:
                payment_id = payment[0]
                customer_id = payment[1]
                payment_value = float(payment[2])
                payment_date = payment[3].strftime("%d.%m.%Y %H:%M:%S")

                total_money += payment_value

                with open(f"{path_to_config_files}Отчет - "
                          f"платежи {date}.txt", 'a+', encoding='utf-8') as payments_report_file:
                    payment_report_message = f"id Платежа: {payment_id}\n" \
                                             f"Статус операции: ✅\n" \
                                             f"id Покупателя: {customer_id}\n" \
                                             f"Сумма платежа: {payment_value} RUB 🇷🇺\n" \
                                             f"Дата операции: {payment_date}\n\n" \
                                             f"#########################################\n\n"
                    payments_report_file.write(payment_report_message)

                    total_report_message = "#########################################\n" \
                                           "###################TOTAL#################\n" \
                                           "#########################################\n\n" \
                                           f"Итог на дату {date}: {total_money} RUB 🇷🇺"

            with open(f"{path_to_config_files}Отчет - "
                      f"платежи {date}.txt", 'a+', encoding='utf-8') as payments_report_file:
                payments_report_file.write(total_report_message)

            payments_report_end_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=loading_start.message_id,
                text="<b>Выгрузка платежей закончена</b>",
            )

            await message.answer("<b>Открываю панель администратора</b>", reply_markup=admin_keyboard)

            await bot.send_document(
                message.from_user.id,
                open(f"{path_to_config_files}Отчет - платежи {date}.txt"),
                caption=f"✅ <b>Сбор информации о платежах закончен</b>\n\n"
                        f"<b>Начало сбора:</b> {payments_report_start_time}\n"
                        f"<b>Конец сбора:</b> {payments_report_end_time}\n\n"
                        f"<b>Итог:</b> {total_money} RUB 🇷🇺\n\n"
                        f"<code>Прикрепляю отчет по платежам на дату {date}</code>"
            )

            await state.finish()
        else:
            await message.answer(f"⚠️ <b>Платежных операций для даты {searching_date} "
                                 f"не обнаружено</b>", reply_markup=admin_keyboard)
            await state.finish()

        await state.finish()
    else:
        await message.answer("⚠️ <b>Просмотр доходов по дате отменен</b>", reply_markup=admin_keyboard)
        await state.finish()


async def get_payments_period(callback_query: types.CallbackQuery):
    message = callback_query.message

    await callback_query.answer("Загрузка...")
    await message.edit_text("<b>Просмотр доходов за период</b>")

    await message.answer("📅 <b>Введите период, доход которого вас интересует</b>\n\n"
                         "Период вводится в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ, (другой не "
                         "принимается) где первая дата - начало периода, а вторая, соответсвенно, конец\n\n"
                         "<code>Для отмены операции нажмите на кнопку \"Отменить\"</code>",
                         reply_markup=back_admin_keyboard)

    await GetPaymentPeriodState.waiting_for_period.set()


@is_cancel
async def get_payments_period_choosing(message: types.Message, state: FSMContext):
    period = message.text

    try:
        dates = period.split(' - ')
        [date.strip() for date in dates]

        start_period_date = convert_to_date(dates[0]).strftime("%d.%m.%Y")
        end_period_date = convert_to_date(dates[1]).strftime("%d.%m.%Y")
    except:
        await message.answer("⚠️ <b>Провертье формат ввода даты</b>\n\n"
                             f"<code>Вы ввели: {period}</code>\n\n"
                             "<code>Нужно: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ</code>\n\n"
                             "<code>Попробуйте снова</code>")
        return

    await message.answer("<b>Открыл панель администатора</b>", reply_markup=admin_keyboard)

    await message.answer(start_period_date)
    await message.answer(end_period_date, reply_markup=menu_keyboard)

    await state.finish()


def register_handlers_admin_payments(dp: Dispatcher):
    dp.register_callback_query_handler(
        get_payments,
        lambda callback_query: callback_query.data and callback_query.data == "admin_payments_get"
    )
    dp.register_callback_query_handler(
        get_payment_date,
        lambda callback_query: callback_query.data and callback_query.data == "admin_payments_date_get",
        state=None
    )
    dp.register_message_handler(
        get_payment_date_choosing,
        content_types=['text'], state=GetPaymentsDateState.waiting_for_date
    )
    dp.register_callback_query_handler(
        get_payments_period,
        lambda callback_query: callback_query.data and callback_query.data == "admin_payments_period_get",
        state=None
    )
    dp.register_message_handler(
        get_payments_period_choosing,
        content_types=['text'], state=GetPaymentPeriodState.waiting_for_period
    )
