from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class User:
    id: Optional[int]
    phone_number: str
    full_name: str
    email: Optional[str]
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    backup_codes: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

@dataclass
class OTPVerification:
    id: Optional[int]
    phone_number: str
    otp_code: str
    purpose: str  # 'registration', 'login', 'password_reset'
    expires_at: datetime
    is_used: bool = False
    created_at: Optional[datetime] = None

@dataclass
class MFASetup:
    secret: str
    qr_code: str
    backup_codes: Optional[List[str]] = None