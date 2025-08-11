from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.service import Service


class ServiceRepository(ABC):
    @abstractmethod
    async def create(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    async def get_by_id(self, service_id: int) -> Optional[Service]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Service]:
        pass
    
    @abstractmethod
    async def get_all(self, active_only: bool = True) -> List[Service]:
        pass
    
    @abstractmethod
    async def update(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    async def delete(self, service_id: int) -> bool:
        pass