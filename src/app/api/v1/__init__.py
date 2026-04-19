from fastapi import APIRouter

from .entries import router as entries_router
from .photos import router as photos_router

router = APIRouter()
router.include_router(entries_router, prefix="/entries", tags=["entries"])
router.include_router(photos_router, prefix="/photos", tags=["photos"])
