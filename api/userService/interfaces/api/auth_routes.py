from fastapi import APIRouter, Depends, HTTPException, status

from interfaces.schemas.user_schemas import (
    UserCreateRequest, UserLoginRequest, UserResponse, TokenResponse,
    OTPRequest, OTPVerifyRequest, OTPResponse, MessageResponse,
    PasswordResetRequest
)
from interfaces.dependencies import (
    get_user_registration_use_case, get_user_login_use_case,
    get_request_otp_use_case, get_verify_otp_use_case,
    get_reset_password_use_case
)
from application.use_cases.user_use_cases import (
    UserRegistrationUseCase, UserLoginUseCase,
    RequestOTPUseCase, VerifyOTPUseCase, ResetPasswordUseCase
)
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreateRequest,
    use_case: UserRegistrationUseCase = Depends(get_user_registration_use_case)
):
    """Register a new user"""
    try:
        result = await use_case.execute(
            phone_number=user_data.phone_number,
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password,
            role_id=user_data.role_id
        )
        
        user = result['user']
        roles = result['roles']
        
        return UserResponse(
            id=user.id,
            phone_number=user.phone_number,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            roles=roles
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    otp_request: OTPRequest,
    use_case: RequestOTPUseCase = Depends(get_request_otp_use_case)
):
    """Request OTP for registration, login, or password reset"""
    try:
        otp_code = await use_case.execute(otp_request.phone_number, otp_request.purpose)
        return OTPResponse(
            message="OTP sent successfully",
            otp=otp_code  # Remove this in production
        )
    except ValueError as e:
        if "User already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        elif "User not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(
    otp_verify: OTPVerifyRequest,
    use_case: VerifyOTPUseCase = Depends(get_verify_otp_use_case)
):
    """Verify OTP"""
    try:
        await use_case.execute(otp_verify.phone_number, otp_verify.otp_code, otp_verify.purpose)
        return MessageResponse(message="OTP verified successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    user_login: UserLoginRequest,
    use_case: UserLoginUseCase = Depends(get_user_login_use_case)
):
    """Login with phone number, password, and mandatory MFA code"""
    try:
        result = await use_case.execute(
            phone_number=user_login.phone_number,
            password=user_login.password,
            mfa_code=user_login.mfa_code
        )
        
        user_response = UserResponse(
            id=result["user"].id,
            phone_number=result["user"].phone_number,
            full_name=result["user"].full_name,
            email=result["user"].email,
            is_active=result["user"].is_active,
            is_verified=result["user"].is_verified,
            mfa_enabled=result["user"].mfa_enabled,
            created_at=result["user"].created_at,
            last_login=result["user"].last_login
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
    except ValueError as e:
        if "Invalid phone number or password" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        elif "deactivated" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        elif "MFA" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    password_reset: PasswordResetRequest,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case)
):
    """Reset password using OTP"""
    try:
        await use_case.execute(
            phone_number=password_reset.phone_number,
            otp_code=password_reset.otp_code,
            new_password=password_reset.new_password
        )
        return MessageResponse(message="Password reset successfully")
    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))