import functools
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache as fastapi_cache
from app.cache.models import RedisCacheKey


CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 minutes


def key_builder(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    service = kwargs["service"]
    redis_key = RedisCacheKey(
        path=request.url.components.path,
        query_params=str(request.query_params),
        service=service,
    )
    return str(redis_key)


def cache():
    def wrapper(func):
        @functools.wraps(func)
        @fastapi_cache(
            expire=CACHE_EXPIRE_IN_SECONDS, coder=PickleCoder, key_builder=key_builder
        )
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)

        return inner

    return wrapper
