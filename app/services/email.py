__all__ = (
    'email_service',
    'EmailService',
)

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.config import settings


class EmailService:
    """Email base service."""
    VERIFICATION_EMAIL_SUBJECT = 'Verification'
    SUCCESS_SIGNUP_EMAIL_SUBJECT = 'Success registration'

    def __init__(self):
        self.connection_config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent / 'templates/email'
        )
        self.fast_mail = FastMail(self.connection_config)

    async def send_verification_email(self, email: str, code: int) -> None:
        """Sends verification email to user."""
        message = MessageSchema(
            subject=self.VERIFICATION_EMAIL_SUBJECT,
            recipients=[email],
            tenplate_body={'code': code},
            subtype='html',
        )
        await self.fast_mail.send_message(message, template_name='verification_email.html')

    async def send_success_signup_email(self, email: str, password: str) -> None:
        """Sends success email to user with password after oauth2 flow signup."""
        message = MessageSchema(
            subject=self.SUCCESS_SIGNUP_EMAIL_SUBJECT,
            recipients=[email],
            tenplate_body={'password': password},
            subtype='html',
        )
        await self.fast_mail.send_message(message, template_name='success_signup_email.html')


email_service = EmailService()
