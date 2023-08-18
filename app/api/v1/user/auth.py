import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.user.dependencies import get_current_active_user, get_credentials_payload, get_refresh_token_payload, \
    get_current_active_user_from_refresh_token
from app.core.config import settings
from app.core.errors import ServiceError
from app.core.fastapi.constants import USER_EXISTS_EXCEPTION, USER_DOES_NOT_EXISTS_EXCEPTION
from app.depends import get_services
from app.models.api.auth import TokenResponse
from app.models.api.base import SuccessResponse
from app.models.api.user import EmailRegistration, UserSignup, UserSignin
from app.services.user import UserService
from app.services.verification_code import VerificationCodeService
from app.models.db.user import User


user_auth_router = APIRouter()
logger = logging.getLogger(__name__)


@user_auth_router.post("/email", response_model=SuccessResponse, status_code=HTTPStatus.OK)
async def register_email(
    email: EmailRegistration,
    verification_code_service: VerificationCodeService = Depends(get_services('verification_code_service')),
    user_service: UserService = Depends(get_services('user_service')),
) -> SuccessResponse:
    logger.info(settings.model_dump())
    user = await user_service.get_user_by_login(email=email.email)
    if user:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail=USER_EXISTS_EXCEPTION.format(email=email))
    try:
        await verification_code_service.send_verification_code(email=email.email)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code,
                            detail=str(exc))
    return SuccessResponse()


@user_auth_router.post("/signup", response_model=TokenResponse, status_code=HTTPStatus.OK)
async def signup(
        user_data: UserSignup,
        verification_code_service: VerificationCodeService = Depends(get_services('verification_code_service')),
        user_service: UserService = Depends(get_services('user_service')),
) -> TokenResponse:
    user = await user_service.get_user_by_login(email=user_data.email)
    if user:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail=USER_EXISTS_EXCEPTION.format(email=user_data.email))
    try:
        await verification_code_service.validate_verification_code(email=user_data.email, code=user_data.code)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code,
                            detail=str(exc))

    token_response = await user_service.signup(user_data=user_data)
    return token_response


@user_auth_router.post("/signin", response_model=TokenResponse, status_code=HTTPStatus.OK)
async def signin(
        user_data: UserSignin,
        user_service: UserService = Depends(get_services('user_service')),
) -> TokenResponse:
    user = await user_service.get_user_by_login(email=user_data.email)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail=USER_DOES_NOT_EXISTS_EXCEPTION.format(email=user_data.email))

    try:
        token_response = await user_service.signin(user_data=user_data)
        return token_response
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code,
                            detail=str(exc))


@user_auth_router.post("/logout", response_model=SuccessResponse, status_code=HTTPStatus.OK)
async def logout(
        user: Annotated[User, Depends(get_current_active_user)],
        token_payload: Annotated[dict, Depends(get_credentials_payload)],
        user_service: UserService = Depends(get_services('user_service')),
) -> SuccessResponse:
    await user_service.logout(user_id=user.id, access_token_id=token_payload['jti'])
    return SuccessResponse()


@user_auth_router.post("/refresh", response_model=TokenResponse, status_code=HTTPStatus.OK)
async def refresh(
        user: Annotated[User, Depends(get_current_active_user_from_refresh_token)],
        refresh_token_payload: Annotated[dict, Depends(get_refresh_token_payload)],
        user_service: UserService = Depends(get_services('user_service')),
) -> TokenResponse:
    token_response = await user_service.refresh_token_pair(user=user, access_token_id=refresh_token_payload['jti'])
    return token_response
