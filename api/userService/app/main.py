from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine
from infrastructure.db.models import UserModel, OTPVerificationModel
from interfaces.api.routes import router

# Create database tables
UserModel.metadata.create_all(bind=engine)
OTPVerificationModel.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="User management service with phone number authentication and mandatory MFA",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)