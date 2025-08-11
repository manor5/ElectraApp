from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from domain.models.user_role import UserRole
from domain.repositories.user_role_repository import UserRoleRepository
from infrastructure.db.models.user_role import UserRoleModel
from .base_repository import BaseRepository


class UserRoleRepositoryImpl(BaseRepository, UserRoleRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def create(self, user_role: UserRole) -> UserRole:
        db_role = UserRoleModel(
            name=user_role.name,
            description=user_role.description,
            is_active=user_role.is_active
        )
        self.session.add(db_role)
        await self.session.commit()
        await self.session.refresh(db_role)
        return self._model_to_domain(db_role)
    
    async def get_by_id(self, role_id: int) -> Optional[UserRole]:
        stmt = select(UserRoleModel).where(UserRoleModel.id == role_id)
        result = await self.session.execute(stmt)
        db_role = result.scalar_one_or_none()
        return self._model_to_domain(db_role) if db_role else None
    
    async def get_by_name(self, name: str) -> Optional[UserRole]:
        stmt = select(UserRoleModel).where(UserRoleModel.name == name)
        result = await self.session.execute(stmt)
        db_role = result.scalar_one_or_none()
        return self._model_to_domain(db_role) if db_role else None
    
    async def get_all(self, active_only: bool = True) -> List[UserRole]:
        stmt = select(UserRoleModel)
        if active_only:
            stmt = stmt.where(UserRoleModel.is_active == True)
        result = await self.session.execute(stmt)
        db_roles = result.scalars().all()
        return [self._model_to_domain(role) for role in db_roles]
    
    async def update(self, user_role: UserRole) -> UserRole:
        stmt = (
            update(UserRoleModel)
            .where(UserRoleModel.id == user_role.id)
            .values(
                name=user_role.name,
                description=user_role.description,
                is_active=user_role.is_active
            )
            .returning(UserRoleModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        db_role = result.scalar_one()
        return self._model_to_domain(db_role)
    
    async def delete(self, role_id: int) -> bool:
        stmt = delete(UserRoleModel).where(UserRoleModel.id == role_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    def _model_to_domain(self, db_role: UserRoleModel) -> UserRole:
        return UserRole(
            id=db_role.id,
            name=db_role.name,
            description=db_role.description,
            is_active=db_role.is_active,
            created_at=db_role.created_at,
            updated_at=db_role.updated_at
        )