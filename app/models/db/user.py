__all__ = (
    'User',
    'VerificationCode',
)

from typing import Dict

from passlib.context import CryptContext
from tortoise import fields
from tortoise.models import Model

from app.models.db.base import AbstractDates

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    __module__ = 'user'

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=128)

    last_login = fields.DatetimeField(default=None, null=True)
    is_superuser = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    date_joined = fields.DatetimeField(auto_now_add=True)

    class Meta:
        app = 'user'
        table = 'user_user'

    def __str__(self) -> str:
        return f'User(id={self.id}, email={self.email}, is_active={self.is_active})'

    def to_dict(self) -> Dict:
        return {
            'id': self.id,  # type: ignore # noqa
            'email': self.email,  # type: ignore # noqa
            'first_name': self.first_name,  # type: ignore # noqa
            'last_name': self.last_name,  # type: ignore # noqa
            'initials': self.initials,  # type: ignore # noqa
        }

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verifies password with stores hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Gets hash for plain password."""
        return pwd_context.hash(password)


class VerificationCode(AbstractDates):
    """User verification code."""
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    code = fields.IntField(unique=True)
    expiration_at = fields.DatetimeField()

    class Meta:
        app = 'user'
        table = 'verification_code'

    def __str__(self) -> str:
        return f'VerificationCode(email={self.email}, code={self.code}, expiration_at={self.expiration_at})'
