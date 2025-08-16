from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from domain.models.service import Service
from domain.repositories.service_repository import ServiceRepository
from infrastructure.db.models.service import ServiceModel
from .base_repository import BaseRepository


class ServiceRepositoryImpl(BaseRepository[Service, ServiceModel], ServiceRepository):
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def create(self, service: Service) -> Service:
        db_service = self._to_database(service)
        db_service = self._commit_and_refresh(db_service)
        return self._to_domain(db_service)
    
    async def get_by_id(self, service_id: int) -> Optional[Service]:
        db_service = self.db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        return self._to_domain(db_service) if db_service else None
    
    async def get_by_name(self, name: str) -> Optional[Service]:
        db_service = self.db.query(ServiceModel).filter(ServiceModel.name == name).first()
        return self._to_domain(db_service) if db_service else None
    
    async def get_all(self, active_only: bool = True) -> List[Service]:
        query = self.db.query(ServiceModel)
        if active_only:
            query = query.filter(ServiceModel.is_active == True)
        db_services = query.all()
        return [self._to_domain(service) for service in db_services]
    
    async def update(self, service: Service) -> Service:
        db_service = self.db.query(ServiceModel).filter(ServiceModel.id == service.id).first()
        if db_service:
            db_service.name = service.name
            db_service.description = service.description
            db_service.is_active = service.is_active
            if self._safe_commit():
                return self._to_domain(db_service)
        raise ValueError("Service not found or update failed")
    
    async def delete(self, service_id: int) -> bool:
        db_service = self.db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if db_service:
            self.db.delete(db_service)
            return self._safe_commit()
        return False
    
    def _to_domain(self, db_service: ServiceModel) -> Service:
        """Convert database model to domain model"""
        return Service(
            id=db_service.id,
            name=db_service.name,
            description=db_service.description,
            is_active=db_service.is_active,
            created_at=db_service.created_at,
            updated_at=db_service.updated_at
        )
    
    def _to_database(self, service: Service) -> ServiceModel:
        """Convert domain model to database model"""
        return ServiceModel(
            id=service.id,
            name=service.name,
            description=service.description,
            is_active=service.is_active,
            created_at=service.created_at,
            updated_at=service.updated_at
        )