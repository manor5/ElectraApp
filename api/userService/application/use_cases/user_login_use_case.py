from datetime import datetime
from typing import Optional

from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.services.auth_service import AuthService, MFAService


class UserLoginUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, phone_number: str, password: str, mfa_code: Optional[str] = None) -> dict:
        # Get user
        user = await self.user_repo.get_by_phone_number(phone_number)
        if not user or not AuthService.verify_password(password, user.hashed_password):
            raise ValueError("Invalid phone number or password")

        if not user.is_active:
            raise ValueError("User account is deactivated")

        # Mandatory MFA check
        if not user.mfa_enabled:
            raise ValueError("MFA must be enabled. Please setup MFA first.")

        if not mfa_code:
            raise ValueError("MFA code is required")

        # Verify MFA
        is_valid_mfa = False
        if user.mfa_secret:
            is_valid_mfa = MFAService.verify_totp(user.mfa_secret, mfa_code)

        # Check backup codes if TOTP fails
        if not is_valid_mfa and user.backup_codes:
            if mfa_code.upper() in user.backup_codes:
                # Remove used backup code
                user.backup_codes.remove(mfa_code.upper())
                await self.user_repo.update(user)
                is_valid_mfa = True

        if not is_valid_mfa:
            raise ValueError("Invalid MFA code")

        # Update last login
        user.last_login = datetime.utcnow()
        await self.user_repo.update(user)

        # Create access token
        access_token = AuthService.create_access_token(
            data={"sub": user.phone_number, "role": user.role.value}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }