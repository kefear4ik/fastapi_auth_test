__all__ = ('JwtTokenTypeEnum',)

from app.core.enums.base import BaseStrEnum


class JwtTokenTypeEnum(BaseStrEnum):
    access = 'access'
    refresh = 'refresh'
