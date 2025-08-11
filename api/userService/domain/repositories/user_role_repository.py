from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.user_role import UserRole


class UserRoleRepository(ABC):
    @abstractmethod
    async def create(self, user_role: UserRole) -> UserRole:
        pass
    
    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[UserRole]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[UserRole]:
        pass
    
    @abstractmethod
    async def get_all(self, active_only: bool = True) -> List[UserRole]:
        pass
    
    @abstractmethod
    async def update(self, user_role: UserRole) -> UserRole:
        pass
    
    @abstractmethod
    async def delete(self, role_id: int) -> bool:
        pass