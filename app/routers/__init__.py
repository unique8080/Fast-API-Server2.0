from fastapi import APIRouter
from .csv_handler import router as csv_router
from .logging_handler import router as logging_router

router = APIRouter()

# Include routers without prefix to avoid empty path issues
router.include_router(csv_router, prefix="/files")
router.include_router(logging_router, prefix="/logs")
