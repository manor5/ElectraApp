from fastapi import APIRouter, Depends, HTTPException, status

from domain.models.user import User
from interfaces.schemas.user_schemas import (
    MFASetupResponse, MFAEnableRequest, MFAEnableResponse
)
from interfaces.dependencies import (
    get_current_user, get_setup_mfa_use_case, get_enable_mfa_use_case
)
from application.use_cases.user_use_cases import SetupMFAUseCase, EnableMFAUseCase

router = APIRouter(prefix="/mfa", tags=["Multi-Factor Authentication"])

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    use_case: SetupMFAUseCase = Depends(get_setup_mfa_use_case)
):
    """Setup MFA for current user"""
    try:
        result = await use_case.execute(current_user.id)
        return MFASetupResponse(secret=result.secret, qr_code=result.qr_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/enable", response_model=MFAEnableResponse)
async def enable_mfa(
    mfa_enable: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    use_case: EnableMFAUseCase = Depends(get_enable_mfa_use_case)
):
    """Enable MFA for current user (mandatory)"""
    try:
        backup_codes = await use_case.execute(current_user.id, mfa_enable.totp_code)
        return MFAEnableResponse(
            message="MFA enabled successfully. Save these backup codes in a secure location.",
            backup_codes=backup_codes
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))