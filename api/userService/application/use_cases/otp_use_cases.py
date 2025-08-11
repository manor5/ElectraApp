from datetime import datetime, timedelta

from domain.models.user import OTPVerification
from domain.repositories.user_repository import UserRepository, OTPRepository
from infrastructure.services.auth_service import OTPService, PhoneService


class RequestOTPUseCase:
    def __init__(self, user_repo: UserRepository, otp_repo: OTPRepository):
        self.user_repo = user_repo
        self.otp_repo = otp_repo

    async def execute(self, phone_number: str, purpose: str) -> str:
        # Validate purpose
        if purpose not in ["registration", "login", "password_reset"]:
            raise ValueError("Invalid OTP purpose")

        # For registration, check if user doesn't exist
        if purpose == "registration":
            existing_user = await self.user_repo.get_by_phone_number(phone_number)
            if existing_user:
                raise ValueError("User already exists")

        # For login/password reset, check if user exists
        elif purpose in ["login", "password_reset"]:
            user = await self.user_repo.get_by_phone_number(phone_number)
            if not user:
                raise ValueError("User not found")

        # Generate and store OTP
        otp_code = OTPService.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        otp = OTPVerification(
            id=None,
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )

        await self.otp_repo.create(otp)

        # Send OTP via SMS
        PhoneService.send_otp(phone_number, otp_code)

        return otp_code  # Remove this in production


class VerifyOTPUseCase:
    def __init__(self, otp_repo: OTPRepository):
        self.otp_repo = otp_repo

    async def execute(self, phone_number: str, otp_code: str, purpose: str) -> bool:
        otp = await self.otp_repo.get_by_phone_and_purpose(phone_number, purpose)
        
        if not otp:
            raise ValueError("Invalid or expired OTP")

        if OTPService.is_expired(otp.created_at):
            raise ValueError("OTP has expired")

        if otp.otp_code != otp_code:
            raise ValueError("Invalid OTP code")

        # Mark as used
        await self.otp_repo.mark_as_used(otp.id)
        return True