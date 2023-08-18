from fastapi import APIRouter

from app.api.v1.user.auth import user_auth_router

user_router = APIRouter()

user_router.include_router(user_auth_router, prefix="/auth", tags=["auth"])
