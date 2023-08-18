__all__ = (
    'generate_jwt_keys',
)

import os
import logging

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from app.core.config import settings


logger = logging.getLogger(__name__)


def generate_jwt_keys() -> None:
    logger.info('Preparing jwt keys....')

    public_exponent = 65537
    key_size = 2048
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=public_exponent,
        key_size=key_size
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )

    jwt_keys_dir = os.path.abspath(str(settings.JWT_KEYS_DIR))

    private_key_filename = os.path.join(jwt_keys_dir, settings.JWT_PRIVATE_KEY_NAME)
    public_key_filename = os.path.join(jwt_keys_dir, settings.JWT_PUBLIC_KEY_NAME)
    os.makedirs(jwt_keys_dir, exist_ok=True)

    if not os.path.exists(private_key_filename) or not os.path.exists(public_key_filename):
        with open(private_key_filename, "wb") as file_out:
            file_out.write(private_key)

        with open(public_key_filename, "wb") as file_out:
            file_out.write(public_key)

    return None
