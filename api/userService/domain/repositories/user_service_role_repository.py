from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.user_service_role import UserServiceRole


class UserServiceRoleRepository(ABC):
    @abstractmethod
    async def create(self, user_service_role: UserServiceRole) -> UserServiceRole:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[UserServiceRole]:
        pass
    
    @abstractmethod
    async def get_user_roles_in_service(self, user_id: int, service_id: int) -> List[UserServiceRole]:
        pass
    
    @abstractmethod
    async def get_user_services(self, user_id: int, active_only: bool = True) -> List[UserServiceRole]:
        pass
    
    @abstractmethod
    async def get_service_users(self, service_id: int, role_id: Optional[int] = None, active_only: bool = True) -> List[UserServiceRole]:
        pass
    
    @abstractmethod
    async def user_has_role_in_service(self, user_id: int, service_id: int, role_id: int) -> bool:
        pass
    
    @abstractmethod
    async def get_user_role_in_service(self, user_id: int, service_id: int) -> Optional[UserServiceRole]:
        pass
    
    @abstractmethod
    async def update_user_role_in_service(self, user_id: int, service_id: int, new_role_id: int) -> UserServiceRole:
        pass
    
    @abstractmethod
    async def update(self, user_service_role: UserServiceRole) -> UserServiceRole:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
    
    @abstractmethod
    async def deactivate_user_service_role(self, user_id: int, service_id: int) -> bool:
        pass