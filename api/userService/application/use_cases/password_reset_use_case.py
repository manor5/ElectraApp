from domain.repositories.user_repository import UserRepository, OTPRepository
from infrastructure.services.auth_service import AuthService
from .otp_use_cases import VerifyOTPUseCase


class ResetPasswordUseCase:
    def __init__(self, user_repo: UserRepository, otp_repo: OTPRepository):
        self.user_repo = user_repo
        self.otp_repo = otp_repo

    async def execute(self, phone_number: str, otp_code: str, new_password: str) -> bool:
        # Verify OTP
        verify_otp_use_case = VerifyOTPUseCase(self.otp_repo)
        await verify_otp_use_case.execute(phone_number, otp_code, "password_reset")

        # Get user and update password
        user = await self.user_repo.get_by_phone_number(phone_number)
        if not user:
            raise ValueError("User not found")

        user.hashed_password = AuthService.hash_password(new_password)
        await self.user_repo.update(user)

        return True