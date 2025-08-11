import phonenumbers
from typing import Optional

from domain.models.user import User
from domain.repositories.user_repository import UserRepository, OTPRepository
from domain.repositories.user_service_role_repository import UserServiceRoleRepository
from domain.models.user_service_role import UserServiceRole
from infrastructure.services.auth_service import AuthService


class UserRegistrationUseCase:
    def __init__(self, user_repo: UserRepository, otp_repo: OTPRepository, 
                 user_service_role_repo: UserServiceRoleRepository):
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.user_service_role_repo = user_service_role_repo

    async def execute(self, phone_number: str, full_name: str, email: Optional[str], 
                     password: str, role_id: Optional[int] = None, service_id: int = 1) -> dict:
        # Validate phone number
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")
            formatted_phone = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError("Invalid phone number format")

        # Check if user already exists
        existing_user = await self.user_repo.get_by_phone_number(formatted_phone)
        if existing_user:
            raise ValueError("User with this phone number already exists")

        if email:
            existing_email = await self.user_repo.get_by_email(email)
            if existing_email:
                raise ValueError("User with this email already exists")

        # Create user first
        hashed_password = AuthService.hash_password(password)
        user = User(
            id=None,
            phone_number=formatted_phone,
            full_name=full_name,
            email=email,
            hashed_password=hashed_password
        )

        created_user = await self.user_repo.create(user)
        
        # Assign role if provided (default to role_id=2 which is "user" role)
        if role_id is None:
            role_id = 2  # Default "user" role

        # Create UserServiceRole for the specified service (handles unique constraint)
        try:
            user_service_role = UserServiceRole(
                id=None,
                user_id=created_user.id,
                service_id=service_id,  # Default to userService (id=1)
                role_id=role_id,
                is_active=True
            )
            await self.user_service_role_repo.create(user_service_role)
        except Exception as e:
            # If there's a unique constraint violation, it means user already has a role in this service
            # This shouldn't happen in registration, but we handle it gracefully
            if "uq_user_service" in str(e):
                raise ValueError(f"User already has a role assigned in service {service_id}")
            raise e

        # Get user with populated roles
        db_user_with_roles = await self.user_repo.get_by_id_with_roles(created_user.id)
        return self.user_repo.db_user_to_response_dict(db_user_with_roles)