__all__ = (
    'User',
    'UserVerificationCode',
    'EmailRegistration',
    'UserSignup',
    'UserSignin',
    'RefreshToken',
)

from datetime import datetime

from password_validation import PasswordPolicy
from pydantic import BaseModel, EmailStr, field_validator


password_policy = PasswordPolicy(
    lowercase=1,
    uppercase=1,
    numbers=1,
    min_length=8,
    max_length=20,
)


class User(BaseModel):
    id: int
    email: str
    username: str
    password: str
    last_login: datetime

    class Config:
        use_enum_values = True


class UserVerificationCode(BaseModel):
    code: str

    class Config:
        use_enum_values = True


class EmailRegistration(BaseModel):
    email: EmailStr


class UserSignup(BaseModel):
    email: EmailStr
    code: int
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        _validate_password = password_policy.validate(password=v)
        if not _validate_password:
            errors = ''.join(
                [f"{exc.name} not satisfied: expected: {exc.requirement}, got: {exc.actual}. ".capitalize()
                 for exc in password_policy.test_password(v)]
            )
            raise ValueError(errors)
        return v


class UserSignin(BaseModel):
    email: EmailStr
    password: str


class RefreshToken(BaseModel):
    refresh_token: str
