from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from domain.models.service import Service
from domain.repositories.service_repository import ServiceRepository
from infrastructure.db.models.service import ServiceModel
from .base_repository import BaseRepository


class ServiceRepositoryImpl(BaseRepository, ServiceRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def create(self, service: Service) -> Service:
        db_service = ServiceModel(
            name=service.name,
            description=service.description,
            is_active=service.is_active
        )
        self.session.add(db_service)
        await self.session.commit()
        await self.session.refresh(db_service)
        return self._model_to_domain(db_service)
    
    async def get_by_id(self, service_id: int) -> Optional[Service]:
        stmt = select(ServiceModel).where(ServiceModel.id == service_id)
        result = await self.session.execute(stmt)
        db_service = result.scalar_one_or_none()
        return self._model_to_domain(db_service) if db_service else None
    
    async def get_by_name(self, name: str) -> Optional[Service]:
        stmt = select(ServiceModel).where(ServiceModel.name == name)
        result = await self.session.execute(stmt)
        db_service = result.scalar_one_or_none()
        return self._model_to_domain(db_service) if db_service else None
    
    async def get_all(self, active_only: bool = True) -> List[Service]:
        stmt = select(ServiceModel)
        if active_only:
            stmt = stmt.where(ServiceModel.is_active == True)
        result = await self.session.execute(stmt)
        db_services = result.scalars().all()
        return [self._model_to_domain(service) for service in db_services]
    
    async def update(self, service: Service) -> Service:
        stmt = (
            update(ServiceModel)
            .where(ServiceModel.id == service.id)
            .values(
                name=service.name,
                description=service.description,
                is_active=service.is_active
            )
            .returning(ServiceModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        db_service = result.scalar_one()
        return self._model_to_domain(db_service)
    
    async def delete(self, service_id: int) -> bool:
        stmt = delete(ServiceModel).where(ServiceModel.id == service_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    def _model_to_domain(self, db_service: ServiceModel) -> Service:
        return Service(
            id=db_service.id,
            name=db_service.name,
            description=db_service.description,
            is_active=db_service.is_active,
            created_at=db_service.created_at,
            updated_at=db_service.updated_at
        )