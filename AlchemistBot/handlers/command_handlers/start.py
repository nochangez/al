# coding=utf-8


from random import randint

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from services.help.decorators import *
from keyboards.reply_keyboards.menu import *
from keyboards.inline_keyboards.cities import *
from data.config import redis_helper, init_cities
from services.project.user_controller import UserController


class Captcha(StatesGroup):
    waiting_for_answer = State()


@is_subscriber
async def process_start_command(message: types.Message, state: FSMContext):
    await state.finish()

    cities = await init_cities()

    cities_keyboard = await cities_keys_init()

    user_controller = UserController()
    captcha_status = await redis_helper.redis_lrange('captcha_status', 0, 1)

    if len(captcha_status) != 0:
        await state.finish()

        if captcha_status[0].decode('utf-8') == message.from_user.id:
            captcha = await redis_helper.redis_lrange('captcha_status', 0, 1)
            print(captcha)

            is_registered = await user_controller.is_user(user_id=message.from_user.id)
            if not is_registered:
                await message.answer(cities)
                await message.answer("<b>Выберите город:</b>", reply_markup=cities_keyboard)
            else:
                welcome_message = "🧪 Добро пожаловать в <b>Алхимик SHOP</b> ✨\n\n" \
                                  "🌈 Только мы <u>раздаем бесплатно</u> клад 🔥"

                await message.answer(welcome_message, reply_markup=menu_keyboard)
        else:
            is_registered = await user_controller.is_user(user_id=message.from_user.id)
            if not is_registered:
                await message.answer("<b>Выберите город:</b>", reply_markup=cities_keyboard)
            else:
                welcome_message = "🧪 Добро пожаловать в <b>Алхимик SHOP</b> ✨\n\n" \
                                  "🌈 Только мы <u>раздаем бесплатно</u> клад 🔥"

                await message.answer(welcome_message, reply_markup=menu_keyboard)
    else:
        first_number = randint(1, 25)
        second_number = randint(1, 25)

        result = first_number + second_number
        await redis_helper.redis_set('result', result)

        example = f"{first_number} + {second_number} = ?"
        make_example_message = f"Чтобы продолжить работу с ботом, решите пример:\n\n" \
                               f"<b>{example}</b>"

        await message.answer(make_example_message)

        await Captcha.waiting_for_answer.set()


@is_subscriber
async def get_answer(message: types.Message, state: FSMContext):
    user_answer = message.text
    result = await redis_helper.decode_bytes(
        await redis_helper.redis_get('result')
    )

    cities_keyboard = await cities_keys_init()

    if str(result) == str(user_answer):
        await redis_helper.redis_lpush('captcha_status', ['true', message.from_user.id])
        await redis_helper.redis_expire('captcha_status', 3600)

        user_controller = UserController()

        is_registered = await user_controller.is_user(user_id=message.from_user.id)
        if is_registered:
            welcome_message = "🧪 Добро пожаловать в <b>Алхимик SHOP</b> ✨\n\n" \
                              "🌈 Только мы <u>раздаем бесплатно</u> клад 🔥"

            await message.answer(welcome_message, reply_markup=menu_keyboard)
        else:
            await message.answer("<b>Выберите город:</b>", reply_markup=cities_keyboard)
    else:
        print(type(result), type(user_answer))
        await message.answer(f"<b>Неверно!</b>")

    await state.finish()


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'], state=None)
    dp.register_message_handler(process_start_command, Text(equals="🏡 Вернуться в меню"))
    dp.register_message_handler(get_answer, state=Captcha.waiting_for_answer)
