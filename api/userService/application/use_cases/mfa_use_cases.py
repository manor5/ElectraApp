from typing import List

from domain.models.user import MFASetup
from domain.repositories.user_repository import UserRepository
from infrastructure.services.auth_service import MFAService


class SetupMFAUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> MFASetup:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user.mfa_enabled:
            raise ValueError("MFA is already enabled for this user")

        # Generate secret and QR code
        secret = MFAService.generate_secret()
        qr_code = MFAService.generate_qr_code(user.phone_number, secret)

        # Store secret temporarily (not enabled yet)
        user.mfa_secret = secret
        await self.user_repo.update(user)

        return MFASetup(secret=secret, qr_code=qr_code)


class EnableMFAUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: int, totp_code: str) -> List[str]:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.mfa_secret:
            raise ValueError("MFA setup not found. Please setup MFA first.")

        # Verify the TOTP code
        if not MFAService.verify_totp(user.mfa_secret, totp_code):
            raise ValueError("Invalid TOTP code")

        # Generate backup codes
        backup_codes = MFAService.generate_backup_codes()

        # Enable MFA
        user.mfa_enabled = True
        user.backup_codes = backup_codes
        await self.user_repo.update(user)

        return backup_codes