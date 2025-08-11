# Import separated services
from .password_service import PasswordService
from .jwt_service import JWTService
from .mfa_service import MFAService
from .otp_service import OTPService
from .phone_service import PhoneService

# Re-export services for backward compatibility and convenience
__all__ = [
    'PasswordService',
    'JWTService', 
    'MFAService',
    'OTPService',
    'PhoneService',
    'AuthService'
]

class AuthService:
    """
    Facade service that orchestrates authentication-related operations.
    This class provides a unified interface while delegating to specialized services.
    """
    
    # Password operations
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password."""
        return PasswordService.hash_password(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return PasswordService.verify_password(plain_password, hashed_password)
    
    # JWT operations
    @staticmethod
    def create_access_token(data: dict, expires_delta=None) -> str:
        """Create a JWT access token."""
        return JWTService.create_access_token(data, expires_delta)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token."""
        return JWTService.verify_token(token)