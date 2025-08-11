from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from domain.repositories.user_repository import UserRepository, OTPRepository
from domain.repositories.user_service_role_repository import UserServiceRoleRepository
from domain.repositories.user_role_repository import UserRoleRepository
from domain.repositories.service_repository import ServiceRepository
from infrastructure.db.repositories import SQLUserRepository, SQLOTPRepository
from infrastructure.db.user_service_role_repository_impl import UserServiceRoleRepositoryImpl
from infrastructure.db.user_role_repository_impl import UserRoleRepositoryImpl
from infrastructure.db.service_repository_impl import ServiceRepositoryImpl
from infrastructure.services.auth_service import AuthService
from application.use_cases.user_use_cases import (
    UserRegistrationUseCase, UserLoginUseCase, SetupMFAUseCase, EnableMFAUseCase,
    RequestOTPUseCase, VerifyOTPUseCase, ResetPasswordUseCase
)

security = HTTPBearer()

# Repository dependencies
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SQLUserRepository(db)

def get_otp_repository(db: Session = Depends(get_db)) -> OTPRepository:
    return SQLOTPRepository(db)

def get_user_service_role_repository(db: Session = Depends(get_db)) -> UserServiceRoleRepository:
    return UserServiceRoleRepositoryImpl(db)

def get_user_role_repository(db: Session = Depends(get_db)) -> UserRoleRepository:
    return UserRoleRepositoryImpl(db)

def get_service_repository(db: Session = Depends(get_db)) -> ServiceRepository:
    return ServiceRepositoryImpl(db)

# Use case dependencies
def get_user_registration_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    otp_repo: OTPRepository = Depends(get_otp_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
) -> UserRegistrationUseCase:
    return UserRegistrationUseCase(user_repo, otp_repo, user_service_role_repo)

def get_user_login_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserLoginUseCase:
    return UserLoginUseCase(user_repo)

def get_setup_mfa_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> SetupMFAUseCase:
    return SetupMFAUseCase(user_repo)

def get_enable_mfa_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> EnableMFAUseCase:
    return EnableMFAUseCase(user_repo)

def get_request_otp_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    otp_repo: OTPRepository = Depends(get_otp_repository)
) -> RequestOTPUseCase:
    return RequestOTPUseCase(user_repo, otp_repo)

def get_verify_otp_use_case(
    otp_repo: OTPRepository = Depends(get_otp_repository)
) -> VerifyOTPUseCase:
    return VerifyOTPUseCase(otp_repo)

def get_reset_password_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    otp_repo: OTPRepository = Depends(get_otp_repository)
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(user_repo, otp_repo)

# Authentication dependency
async def get_current_user(
    token: str = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository)
):
    try:
        payload = AuthService.verify_token(token.credentials)
        phone_number = payload.get("sub")
        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = await user_repo.get_by_phone_number(phone_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )