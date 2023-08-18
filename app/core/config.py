__all__ = (
    'settings',
    'Settings',
    'models',
)

import os
from datetime import timedelta
from functools import cached_property

from pydantic import PostgresDsn, RedisDsn, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def read_jwt_key(filename: str, jwt_keys_dir: str) -> str:
    jwt_keys_dir = os.path.abspath(str(jwt_keys_dir))
    with open(os.path.join(jwt_keys_dir, str(filename)), 'rb') as fln:
        return fln.read().strip()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fastapi auth test"
    PROJECT_HOST: str = "0.0.0.0"
    PROJECT_PORT: int = 8001

    VERIFICATION_CODE_LENGTH: int = 6
    VERIFICATION_CODE_EXPIRATION_MINUTES: int = 15
    VERIFICATION_CODE_EXPIRATION_DELTA: timedelta = timedelta(minutes=VERIFICATION_CODE_EXPIRATION_MINUTES)

    DEBUG: bool = False

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'test'
    DB_PASSWORD: str = 'test'
    DB_NAME: str = 'test'

    POSTGRES_DSN: PostgresDsn = 'postgres://user:pass@localhost:5432/db_name'
    REDIS_DSN: RedisDsn = 'redis://default:password@redis:6379/0'

    # celery
    CELERY_BROKER_URL: RedisDsn = 'redis://default:password@redis:6379/0'
    CELERY_RESULT_BACKEND: RedisDsn = 'redis://default:password@redis:6379/0'

    # email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    # jwt
    JWT_KEYS_DIR: str = 'jwt_keys'
    JWT_PRIVATE_KEY_NAME: str = 'jwt-key'
    JWT_PUBLIC_KEY_NAME: str = 'jwt-key.pub'
    JWT_ALGORITHM: str = 'RS256'
    JWT_ALLOW_REFRESH: bool = True
    JWT_TOKEN_MAX_AGE: int = 3600
    JWT_REFRESH_TOKEN_EXPIRATION: int = 30
    JWT_LEEWAY: int = 0
    JWT_VERIFY_EXPIRATION: bool = True
    JWT_VERIFY: bool = True
    JWT_AUDIENCE: str = 'fastapi_auth_test'
    JWT_ISSUER: str = 'fastapi_auth_test'

    REFRESH_TOKEN_EXPIRATION: timedelta = timedelta(days=JWT_REFRESH_TOKEN_EXPIRATION)

    @cached_property
    def jwt_private_key(self) -> str:
        return read_jwt_key(self.JWT_PRIVATE_KEY_NAME, self.JWT_KEYS_DIR)

    @cached_property
    def jwt_public_key(self) -> str:
        return read_jwt_key(self.JWT_PUBLIC_KEY_NAME, self.JWT_KEYS_DIR)

    model_config = SettingsConfigDict(
        env_file='.envrc',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
    )


models: list = [
    'app.models',
]

settings = Settings()
