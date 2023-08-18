import datetime
from http import HTTPStatus

from fastapi import HTTPException
from pydantic import EmailStr
from tortoise.transactions import atomic

from app.core.config import settings
from app.core.enums.jwt import JwtTokenTypeEnum
from app.core.errors import UserServiceError
from app.core.fastapi.auth.jwt.jwt import create_jwt_token, ACCESS_TOKEN_SUB, get_jti
from app.core.fastapi.constants import USER_DOES_NOT_EXISTS_EXCEPTION
from app.core.tasks.user import send_success_signup_password
from app.models.api.auth import TokenResponse
from app.models.api.user import UserSignup, UserSignin
from app.models.db.user import User, VerificationCode
from app.services.base import BaseService


class UserService(BaseService):
    @staticmethod
    async def get_user_by_login(email: str) -> User | None:
        return await User.filter(email=email).first()

    @staticmethod
    async def create_user(email: EmailStr, password: str) -> User:
        user = await User.create(email=email,
                                 password=User.get_password_hash(password),
                                 last_login=datetime.datetime.now())
        return user

    async def create_token_pair(self, user: User) -> TokenResponse:
        access_token = create_jwt_token(user_id=user.id,
                                        token_type=JwtTokenTypeEnum.access,
                                        sub=ACCESS_TOKEN_SUB,
                                        email=user.email)
        refresh_token = create_jwt_token(user_id=user.id,
                                         token_type=JwtTokenTypeEnum.refresh,
                                         sub=ACCESS_TOKEN_SUB,
                                         email=user.email)
        await self.storage.set_add(
            key=f'user-refresh-{user.id}',
            value=get_jti(refresh_token),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    @atomic()
    async def signup(self, user_data: UserSignup) -> TokenResponse:
        user = await self.create_user(email=user_data.email, password=user_data.password)
        token_pair = await self.create_token_pair(user=user)
        await VerificationCode.filter(email=user.email).delete()
        send_success_signup_password.delay(email=user.email, password=user_data.password)
        return token_pair

    async def signin(self, user_data: UserSignin) -> TokenResponse:
        user = await self.get_user_by_login(email=user_data.email)
        if not user:
            raise UserServiceError(
                USER_DOES_NOT_EXISTS_EXCEPTION.format(email=user_data.email),
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        if not User.verify_password(plain_password=user_data.password, hashed_password=user.password):
            raise UserServiceError(
                'User password missmatch!',
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        token_pair = await self.create_token_pair(user=user)
        return token_pair

    async def check_access_token_blacklisted(self, access_token_id: str) -> None:
        token = await self.storage.get(key=access_token_id)
        if token is not None:
            raise HTTPException(status_code=400, detail="Inactive access token!")
        return None

    async def add_access_token_to_blacklist(self, access_token_id: str) -> None:
        await self.storage.set(key=access_token_id, value='', exp=settings.JWT_TOKEN_MAX_AGE)
        return None

    async def check_refresh_token_is_active(self, user_id: int, access_token_id: str) -> None:
        token_is_active = await self.storage.value_in_set(key=f'user-refresh-{user_id}', value=access_token_id)
        if not token_is_active:
            raise HTTPException(status_code=400, detail="Inactive refresh token!")
        return None

    async def clean_user_refresh_token_list(self, user_id: int) -> None:
        await self.storage.delete(key=f'user-refresh-{user_id}')
        return None

    async def delete_user_refresh_token(self, user_id: int, access_token_id: str) -> None:
        await self.storage.delete_set_value(key=f'user-refresh-{user_id}', value=access_token_id)
        return None

    async def logout(self, user_id: int, access_token_id: str) -> None:
        await self.add_access_token_to_blacklist(access_token_id=access_token_id)
        await self.clean_user_refresh_token_list(user_id=user_id)
        return None

    async def refresh_token_pair(self, user: User, access_token_id: str) -> TokenResponse:
        await self.delete_user_refresh_token(user_id=user.id, access_token_id=access_token_id)
        token_pair = await self.create_token_pair(user=user)
        return token_pair
