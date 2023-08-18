from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.fastapi.auth.jwt.jwt import jwt_decode_handler
from app.depends import get_services
from app.models.api.user import RefreshToken
from app.models.db import User
from app.services.user import UserService


oauth2_scheme = HTTPBearer()


def get_token_payload(token: str) -> dict:
    try:
        return jwt_decode_handler(token)
    except jwt.exceptions.PyJWTError as exc:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(exc),
            headers={'Authenticate': 'Bearer'},
        )


async def get_credentials_payload(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    return get_token_payload(token=credentials.credentials)


async def get_refresh_token_payload(refresh_token: RefreshToken) -> dict:
    return get_token_payload(token=refresh_token.refresh_token)


async def get_user_from_payload(payload: dict, user_service: UserService) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'Authenticate': 'Bearer'},
    )
    email: str = payload.get('email')
    if email is None:
        raise credentials_exception
    user = await user_service.get_user_by_login(email=email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_credentials(
        payload: dict = Depends(get_credentials_payload),
        user_service: UserService = Depends(get_services('user_service')),
) -> User:
    user = await get_user_from_payload(payload=payload, user_service=user_service)
    await user_service.check_access_token_blacklisted(access_token_id=payload['jti'])
    return user


async def get_current_user_from_refresh_token(
        payload: dict = Depends(get_refresh_token_payload),
        user_service: UserService = Depends(get_services('user_service')),
) -> User:
    user = await get_user_from_payload(payload=payload, user_service=user_service)
    await user_service.check_refresh_token_is_active(user_id=user.id, access_token_id=payload['jti'])
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user_from_credentials)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


async def get_current_active_user_from_refresh_token(
    current_user: Annotated[User, Depends(get_current_user_from_refresh_token)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
