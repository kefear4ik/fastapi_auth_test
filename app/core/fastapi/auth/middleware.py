__all__ = (
    'CustomAuthBackend',
)

import logging
from calendar import timegm

import jwt
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt import InvalidIssuedAtError, ExpiredSignatureError
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from tortoise import timezone
from tortoise.exceptions import DoesNotExist

from app.core.config import settings
from app.core.fastapi.auth.models import CustomUser
from app.models.db import User


logger = logging.getLogger(__name__)
security = HTTPBearer()


class CustomAuthBackend(AuthenticationBackend):

    async def authenticate(self, request):  # noqa
        # Get JWT token from auth header
        authorization: str = request.headers.get('Authorization')
        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme.lower() != 'bearer':
            raise AuthenticationError('Invalid basic auth credentials')

        if not credentials:
            raise AuthenticationError('Invalid basic auth credentials')

        # Checks the validity of the JWT token, if token is invalid returns UnauthenticatedUser object
        try:
            jwt_decoded = jwt.decode(
                credentials,
                settings.JWT_PUBLIC_KEY,
                algorithms=[settings.JWT_ALG]
            )
            self._validate_iat(payload=jwt_decoded, leeway=settings.JWT_LEEWAY)
        except (jwt.PyJWTError, jwt.InvalidAlgorithmError) as exc:
            logger.exception(str(exc))
            raise AuthenticationError('Invalid basic auth credentials')

        try:
            user = await User.get(id=jwt_decoded['user_id'])
        except DoesNotExist:
            logger.exception(
                'User %s or user device %s does not exists!',
                jwt_decoded['user_id'],
                jwt_decoded['device_id'],
            )
            raise AuthenticationError('Invalid basic auth credentials')

        user_description = user.to_dict()

        return AuthCredentials(['authenticated']), CustomUser(**user_description)

    @staticmethod
    def _validate_iat(payload, leeway):
        now = timegm(timezone.now().utctimetuple())
        try:
            iat = int(payload['iat'])
        except ValueError:
            raise InvalidIssuedAtError(
                'Issued At claim (iat) must be an integer.'
            )
        if now - iat - leeway > settings.JWT_MAX_AGE:
            raise ExpiredSignatureError('Signature has expired')
