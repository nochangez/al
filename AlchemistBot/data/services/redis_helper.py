# coding=utf-8


from typing import Any

from redis import Redis
from aiogram.contrib.fsm_storage.redis import RedisStorage2


class RedisHelper:
    def __init__(self):
        # redis connections
        self.redis_client = Redis()  # redis client connection
        self.redis_storage = RedisStorage2()  # redis storage connection

    @staticmethod
    async def decode_bytes(encoded_value: Any) -> Any:
        """
        gets redis byte data and returns decoded data

        :param encoded_value: data to decode
        :return: decoded data, type -> Any
        """

        return encoded_value.decode("utf-8")  # return decoded value

    async def redis_expire(self, name: str, time: int) -> Any:
        return self.redis_client.expire(name=name, time=time)  # set expire key

    async def redis_lpush(self, name: str, values):
        return self.redis_client.lpush(name, *values)

    async def redis_lrange(self, name, start, end):
        return self.redis_client.lrange(name, start, end)

    async def redis_set(self, name: str, value: Any) -> bool:
        """
        creates a note with key data on redis server

        :param name: key name
        :param value: key value
        :return: bool
        """

        return self.redis_client.set(name=name, value=value)  # create key in redis

    async def redis_get(self, name: str) -> bytes:
        """
        this method gets a value from

        :param name: name of a value
        :return: bytes, value from operative memory
        """

        return self.redis_client.get(name=name)  # get data via its name

    async def redis_delete(self, name: str) -> int:
        """
        this method deletes named value from redis

        :param name: name of value
        :return: int
        """

        return self.redis_client.delete(name)

    async def redis_flushall(self) -> bool:
        """
        deletes all keys from redis server

        :return: bool
        """

        return self.redis_client.flushall()  # delete all keys

    async def close_redis_client(self):
        """
        closes redis client

        :return: None
        """

        return self.redis_client.close()

    async def close_redis(self):
        """
        close redis storage and redis client

        :return: list, list of close connections methods
        """

        return [await self.close_redis_client(),
                await self.redis_storage.close(),
                await self.redis_storage.wait_closed()]


# create context manager for RedisHelper
class RedisHelperManager:
    def __init__(self):
        self.__redis_helper = RedisHelper()  # init object for communication with redis helper class

    def __enter__(self):
        """
        create open point for context manager

        :return: RedisHelper() open
        """

        return self.__redis_helper  # enter in context manager and call RedisHelper init

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        create close point for context manager

        :return: RedisHelper() close
        """

        return self.__redis_helper.close_redis()  # exit from context manager and close redis connections
