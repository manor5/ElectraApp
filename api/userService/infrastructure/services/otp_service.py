import secrets
from datetime import datetime, timedelta

from core.config import settings

class OTPService:
    """Service responsible for One-Time Password generation and validation."""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP."""
        return str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
    
    @staticmethod
    def is_expired(created_at: datetime, expires_minutes: int = None) -> bool:
        """Check if an OTP has expired based on creation time."""
        if expires_minutes is None:
            expires_minutes = settings.OTP_EXPIRE_MINUTES
        return datetime.utcnow() > created_at + timedelta(minutes=expires_minutes)