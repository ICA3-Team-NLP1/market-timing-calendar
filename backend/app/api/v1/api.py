from fastapi import APIRouter

from app.api.v1.auth import auth_router
from app.api.v1.users import user_router
from app.api.v1.calendar import calendar_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(user_router, prefix="/users")
api_router.include_router(calendar_router, prefix="/calendar")
