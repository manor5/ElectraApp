from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import datetime
import phonenumbers

# Role and Service response schemas
class UserRoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class UserServiceRoleResponse(BaseModel):
    id: int
    service: ServiceResponse
    role: UserRoleResponse
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Request schemas
class UserCreateRequest(BaseModel):
    phone_number: str
    full_name: str
    email: Optional[str] = None
    password: str
    role_id: Optional[int] = None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        try:
            parsed_number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError('Invalid phone number format')

class UserLoginRequest(BaseModel):
    phone_number: str
    password: str
    mfa_code: Optional[str] = None

class OTPRequest(BaseModel):
    phone_number: str
    purpose: str = Field(..., pattern="^(registration|login|password_reset)$")

class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    purpose: str

class MFAEnableRequest(BaseModel):
    totp_code: str

class PasswordResetRequest(BaseModel):
    phone_number: str
    otp_code: str
    new_password: str

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None

# Response schemas
class UserResponse(BaseModel):
    id: int
    phone_number: str
    full_name: str
    email: Optional[str]
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]
    roles: List[UserServiceRoleResponse] = []
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str

class MFAEnableResponse(BaseModel):
    message: str
    backup_codes: List[str]

class OTPResponse(BaseModel):
    message: str
    otp: Optional[str] = None  # Remove in production

class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str