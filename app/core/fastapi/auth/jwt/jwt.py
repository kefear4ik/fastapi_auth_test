import uuid
from datetime import datetime
from typing import Optional, Union
import jwt

from app.core.config import settings
from app.core.enums.jwt import JwtTokenTypeEnum

ACCESS_TOKEN_SUB = 'access'


def jwt_decode_handler(token: str) -> dict:
    options = {
        'verify_exp': settings.JWT_VERIFY_EXPIRATION,
        'require_iat': True,
        'verify_iat': True,
    }
    return jwt.decode(
        token,
        settings.jwt_public_key,
        verify=settings.JWT_VERIFY,
        options=options,
        leeway=settings.JWT_LEEWAY,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=[settings.JWT_ALGORITHM]
    )


def get_jti(encoded_token: str) -> str:
    """
    Returns the JTI (unique identifier) of an encoded JWT

    :return: string of JTI
    """
    return jwt_decode_handler(token=encoded_token)['jti']


def _jwt_get_iat() -> int:
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())


def _jwt_get_exp(iat: int, token_type: JwtTokenTypeEnum) -> int:
    if token_type == JwtTokenTypeEnum.access:
        return iat + settings.JWT_TOKEN_MAX_AGE
    else:
        return iat + settings.JWT_REFRESH_TOKEN_EXPIRATION * 24 * 60 * 60


def _get_jwt_identifier() -> str:
    return str(uuid.uuid4())


def jwt_payload_handler(
        user_id: int,
        token_type: JwtTokenTypeEnum,
        iat: Optional[int] = None,
        sub: Optional[str] = None,
        email: Optional[str] = None,
        device_id: Optional[str] = None
):

    if iat is None:
        iat = _jwt_get_iat()

    exp = _jwt_get_exp(iat, token_type)

    payload: dict[str, Union[str, int]] = {
        'user_id': user_id,
        'iat': iat,
        'exp': exp,
        'type': token_type.value,
        'jti': _get_jwt_identifier(),
        'iss': settings.JWT_ISSUER,
    }
    if email:
        payload['email'] = email

    if device_id:
        payload['device_id'] = device_id

    # Include original issued at time for a brand-new token,
    # to allow token refresh
    if settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = _jwt_get_iat()

    if settings.JWT_AUDIENCE is not None:
        payload['aud'] = settings.JWT_AUDIENCE

    if sub is not None:
        payload['sub'] = sub

    return payload


def jwt_encode_handler(payload, private_key: Optional[bytes] = None):
    key = private_key or settings.jwt_private_key
    return jwt.encode(
        payload,
        bytes(key),
        settings.JWT_ALGORITHM
    )


def create_jwt_token(
    user_id: int,
    token_type: JwtTokenTypeEnum,
    iat: Optional[int] = None,
    sub: Optional[str] = None,
    private_key: Optional[bytes] = None,
    email: Optional[str] = None,
    device_id: Optional[str] = None,
) -> str:
    payload = jwt_payload_handler(
        user_id=user_id,
        token_type=token_type,
        iat=iat,
        sub=sub,
        email=email,
        device_id=device_id,
    )
    return jwt_encode_handler(payload, private_key=private_key)
