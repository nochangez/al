# coding=utf-8


from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class Captcha(StatesGroup):
    waiting_for_answer = State()


async def captcha_start(message: types.Message):
    pass


async def get_answer(message: types.Message, state: FSMContext):
    pass
