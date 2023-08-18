import logging

from asgiref.sync import async_to_sync

from app.core.celery import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(name='send_verification_code')
def send_verification_code(email: str, code: int) -> None:
    from app.services import email_service
    async_to_sync(email_service.send_verification_email)(email=email, code=code)
    logger.info('Verification email was sent to [%s]', email)
    return None


@celery_app.task(name='send_post_signup_email')
def send_success_signup_password(email: str, password: str) -> None:
    from app.services import email_service
    async_to_sync(email_service.send_success_signup_email)(email=email, password=password)
    logger.info('Post signup email was sent to [%s]', email)
    return None
