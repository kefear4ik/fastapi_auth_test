from redis import asyncio as aioredis
from tortoise import Tortoise

from app import depends
from app.core.config import settings
from app.core.fastapi.auth.jwt.keys import generate_jwt_keys
from app.core.storage import RedisStorage
from app.services import UserService, EmailService
from app.services.verification_code import VerificationCodeService


async def create_pg_connection():
    await Tortoise.init(
        {
            'connections': {
                'default': settings.POSTGRES_DSN.unicode_string()
            },
            'apps': {
                'user': {
                    'models': ['app.models.db.user'],
                },
            }
        }
    )


async def close_pg_connection():
    await Tortoise.close_connections()


async def start_redis():
    depends.redis = aioredis.from_url(settings.REDIS_DSN.unicode_string())


async def close_redis() -> None:
    if depends.redis is not None:
        await depends.redis.close()


async def init_services():
    redis_storage = RedisStorage(depends.redis)
    user_service = UserService(storage=redis_storage)
    verification_code_service = VerificationCodeService
    email_service = EmailService()

    depends.services = {
        'user_service': user_service,
        'verification_code_service': verification_code_service,
        'email_service': email_service,
    }


on_startup = [generate_jwt_keys, create_pg_connection, start_redis, init_services]
on_shutdown = [close_pg_connection, close_redis]
