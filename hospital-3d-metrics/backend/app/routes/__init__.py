# backend/app/routes/__init__.py
from fastapi import APIRouter
from .metrics import router as metrics_router
from app.api.v1.auth import router as auth_router
from .test_admin import router as admin_router
from .test_profile import router as profile_router

api_router = APIRouter()

api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])