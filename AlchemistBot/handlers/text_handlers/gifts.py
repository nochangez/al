# coding=utf-8


from aiogram import Dispatcher, types

from services.project.gifts_controller import GiftsController


gifts_controller = GiftsController()


async def gifts(message: types.Message):
    gift = await gifts_controller.get_gift_info()

    if len(gift) == 0 or gift is None:
        await message.answer("⚠ <b>В твоем городе пока что нет раздач</b>\n\n"
                             "<code>Жди, они скоро появятся!</code>")
    else:
        gift = gift[0]

        gift_text = gift[0]
        coordinates_text = gift[1]

        await message.answer(f"🪨 <b>Раздача клада в твоем городе:</b>\n\n"
                             f"{gift_text}\n\n\n"
                             f"🧭 <b>Координаты:</b>\n\n"
                             f"{coordinates_text}")


def register_handlers_gifts(dp: Dispatcher):
    dp.register_message_handler(
        gifts,
        lambda message: message.text and message.text == "🎁 Раздача товара"
    )
