from fastapi import APIRouter

from .health_routes import router as health_router
from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .mfa_routes import router as mfa_router
from .admin_routes import router as admin_router

# Main router that includes all sub-routers
router = APIRouter()

# Include all route modules
router.include_router(health_router)
router.include_router(auth_router) 
router.include_router(user_router)
router.include_router(mfa_router)
router.include_router(admin_router)