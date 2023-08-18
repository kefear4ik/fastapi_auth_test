from celery import Celery
from app.core.config import settings


celery_app = Celery('fastapi_auth_test')
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
