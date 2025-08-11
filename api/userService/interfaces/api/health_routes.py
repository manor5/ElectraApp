from fastapi import APIRouter

from interfaces.schemas.user_schemas import HealthResponse
from core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/", response_model=HealthResponse)
def read_root():
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )