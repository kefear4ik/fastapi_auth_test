__all__ = ('CacheStorage', 'RedisStorage')

import abc
from typing import Any, Union, Optional

from redis.asyncio.client import Redis


class CacheStorage(abc.ABC):
    @abc.abstractmethod
    async def delete(self, *, key: str) -> Any:
        """Deletes entry from storage by key.

        Args:
            key (str): [description]
        """

    @abc.abstractmethod
    async def set(self, *, key: str, value: Union[str, int] = 0, exp: int) -> Any:
        """Sets data to storage.

        Args:
            key (str | int): key
            value (str): value
                (default value is 0 NOTE: https://stackoverflow.com/a/59292672/2793303)
            exp (int): expiration
        """

    @abc.abstractmethod
    async def get(self, *, key: str) -> Any:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            Any: [description]
        """


class RedisStorage(CacheStorage):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def delete(self, *, key: str) -> Any:
        """Deletes entry from redis by key.

        Args:
            key (str): [description]
        """
        return await self.redis.delete(key)

    async def set(self, *, key: str, value: Union[str, int] = 0, exp: int) -> Any:
        """Sets data to storage.

        Args:
            key (str | int): key
            value (str): value
                (default value is 0 NOTE: https://stackoverflow.com/a/59292672/2793303)
            exp (int): expiration
        """
        return await self.redis.set(key, value, ex=exp)

    async def get(self, *, key: str) -> Any:
        """Gets value by key from redis.

        Args:
            key (str): [description]
        Returns:
            Any: [description]
        """

        return await self.redis.get(key)

    async def read(
            self,
            stream_key: str,
            last_msg_id: Union[bytes, int] = b'$',
            count: Optional[int] = None,
            block: Optional[int] = 0,
    ) -> Any:
        """Reads message from stream with name stream_key

        Args:
            stream_key (str): [name of redis stream]
            last_msg_id (Optional[str]): [last message id]
            count (Optional[int]): [count of messages]
            block (Optional[int]): [number of block]
        Returns:
            Any: [description]
        """
        return await self.redis.xread(
            streams={stream_key: last_msg_id},
            count=count,
            block=block,
        )

    async def send(
            self,
            stream_key: str,
            fields: dict,
    ) -> Any:
        """Sends message to a stream with name stream_key

        Args:
            stream_key (str): [name of redis stream]
            fields (dict): [data to send]
        Returns:
            Any: [description]
        """
        return await self.redis.xadd(stream_key, fields=fields)

    async def set_add(self, key: str, value: str) -> int:
        """Adds value to a set

        Args:
           key (str): [name of set]
           value (str): [value to add to set]
        Returns:
           bool: [add or not add value to set]
        """
        return await self.redis.sadd(key, value)

    async def read_set(self, key: str) -> Any:
        """Gets all the members of the set value stored at key.

        Args:
           key (str): [name of set
        Returns:
           Any: [data from set]
        """
        return await self.redis.smembers(key)

    async def value_in_set(self, key: str, value: str) -> Any:
        """Returns a boolean indicating if ``value`` is a member of set ``name``

        Args:
           key (str): [name of set]
           value (str): [value in set]
        Returns:
           bool: [is value exists]
        """
        return await self.redis.sismember(key, value)

    async def delete_set_value(self, key: str, value: str) -> int:
        """Removes the specified members from the set stored at key

        Args:
           key (str): [name of set]
           value (str): [value to remove from set]
        Returns:
           bool: [remove or not remove value from set]
        """
        return await self.redis.srem(key, value)
