__all__ = (
    'VerificationCodeService',
)

from datetime import datetime, timedelta

from http import HTTPStatus
from pydantic import EmailStr
from tortoise.exceptions import IntegrityError

from app.core.config import settings
from app.core.errors import VerificationCodeServiceError
from app.core.utils import random_with_n_digits
from app.core.tasks.user import send_verification_code
from app.models.db import VerificationCode


class VerificationCodeService:
    @staticmethod
    async def get_verification_code(code: int) -> VerificationCode | None:
        return await VerificationCode.filter(code=code, expiration_at__gt=datetime.now()).first()

    @classmethod
    async def validate_confirmation_code(cls, email: EmailStr, code: int) -> VerificationCode:
        verification_code = await cls.get_verification_code(code=code)
        if not verification_code:
            raise VerificationCodeServiceError(
                'Verification code does not exist!',
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        if verification_code.email != email:
            raise VerificationCodeServiceError(
                'Email and code mismatch!',
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        return verification_code

    @staticmethod
    async def create_verification_code(email: EmailStr, code_expiration: timedelta) -> VerificationCode:
        attempts = 10
        while attempts:
            code = random_with_n_digits(settings.VERIFICATION_CODE_LENGTH)
            try:
                verification_code, _ = await VerificationCode.update_or_create(
                    email=email,
                    defaults={'code': code, 'expiration_at': datetime.now() + code_expiration},
                )
                return verification_code
            except IntegrityError:
                attempts -= 1

        raise VerificationCodeServiceError(
            'Cannot create confirmation sms. Non unique code',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    @classmethod
    async def send_verification_code(cls, email: EmailStr) -> None:
        verification_code = await cls.create_verification_code(
            email=email,
            code_expiration=settings.VERIFICATION_CODE_EXPIRATION_DELTA,
        )
        send_verification_code.delay(email, verification_code.code)
        return None
