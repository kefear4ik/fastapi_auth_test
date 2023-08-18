from typing import List, Tuple

from redis.asyncio import Redis
from fastapi_cache.backends.redis import RedisBackend as BaseRedisBackend


class RedisBackend(BaseRedisBackend):
    def __init__(self, redis_pools: List[Redis]):
        self.__redis_pools = redis_pools

    def get_redis_pool_by_key(self, key: str):
        """Returns redis pool by key"""
        pool_index = hash(key) % len(self.__redis_pools)

        return self.__redis_pools[pool_index]

    async def close_redis_pools(self):
        """
        Safely closes all redis pools
        """
        for redis_pool in self.__redis_pools:
            redis_pool.close()
            await redis_pool.wait_closed()

    @property
    def redis(self) -> Redis:
        return self.get_redis_pool_by_key(self.key)

    async def get(self, key) -> str:
        self.key = key
        return await super().get(key)

    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        self.key = key
        return await super().get_with_ttl(key)

    async def set(self, key: str, value: str, expire: int):
        self.key = key
        return await super().set(key, value, expire=expire)

    async def clear(self, namespace: str, key: str) -> int:
        self.key = key
        return await super().clear(namespace=namespace, key=key)
