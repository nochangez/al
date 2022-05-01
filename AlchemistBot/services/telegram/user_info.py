# coding=utf-8


import json

from telethon import TelegramClient
from telethon.tl.types import PeerUser

from data.config import api_id, api_hash


telegram_client = TelegramClient("alchemist_session_as", api_id=api_id, api_hash=api_hash)


async def get_user_info(user: str):
    try:
        user = int(user)
        return json.loads((await telegram_client.get_entity(PeerUser(user))).to_json())
    except:
        return json.loads((await telegram_client.get_entity(user)).to_json())


async def run_get_user_info(user: str):
    async with telegram_client:
        return await get_user_info(user)
