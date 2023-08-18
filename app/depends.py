from typing import Any, Optional

from redis.asyncio.client import Redis

services: dict[str, Any] = {}
redis: Optional[Redis] = None


def get_services(service: str):
    def _get_services():
        return services[service]

    return _get_services
