from fastapi import APIRouter

from .auth import router as auth_router
from .entries import router as entries_router
from .photos import router as photos_router
from .public import router as public_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(entries_router, prefix="/entries", tags=["entries"])
router.include_router(photos_router, prefix="/photos", tags=["photos"])
router.include_router(public_router, prefix="/public", tags=["public"])
