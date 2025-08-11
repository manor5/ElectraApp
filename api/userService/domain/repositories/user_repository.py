from abc import ABC, abstractmethod
from typing import Optional, List
from ..models.user import User, OTPVerification

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        pass

class OTPRepository(ABC):
    @abstractmethod
    async def create(self, otp: OTPVerification) -> OTPVerification:
        pass
    
    @abstractmethod
    async def get_by_phone_and_purpose(self, phone_number: str, purpose: str) -> Optional[OTPVerification]:
        pass
    
    @abstractmethod
    async def mark_as_used(self, otp_id: int) -> bool:
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        pass