from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import joinedload
from domain.models.user_service_role import UserServiceRole
from domain.repositories.user_service_role_repository import UserServiceRoleRepository
from infrastructure.db.models.user_service_role import UserServiceRoleModel
from .base_repository import BaseRepository


class UserServiceRoleRepositoryImpl(BaseRepository, UserServiceRoleRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def create(self, user_service_role: UserServiceRole) -> UserServiceRole:
        db_usr = UserServiceRoleModel(
            user_id=user_service_role.user_id,
            service_id=user_service_role.service_id,
            role_id=user_service_role.role_id,
            is_active=user_service_role.is_active
        )
        self.session.add(db_usr)
        await self.session.commit()
        await self.session.refresh(db_usr)
        return self._model_to_domain(db_usr)
    
    async def get_by_id(self, id: int) -> Optional[UserServiceRole]:
        stmt = select(UserServiceRoleModel).where(UserServiceRoleModel.id == id)
        result = await self.session.execute(stmt)
        db_usr = result.scalar_one_or_none()
        return self._model_to_domain(db_usr) if db_usr else None

    async def get_user_roles_in_service(self, user_id: int, service_id: int) -> List[UserServiceRole]:
        stmt = select(UserServiceRoleModel).where(
            and_(
                UserServiceRoleModel.user_id == user_id,
                UserServiceRoleModel.service_id == service_id,
                UserServiceRoleModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        db_usrs = result.scalars().all()
        return [self._model_to_domain(usr) for usr in db_usrs]

    async def get_user_services(self, user_id: int, active_only: bool = True) -> List[UserServiceRole]:
        stmt = select(UserServiceRoleModel).where(UserServiceRoleModel.user_id == user_id)
        if active_only:
            stmt = stmt.where(UserServiceRoleModel.is_active == True)
        result = await self.session.execute(stmt)
        db_usrs = result.scalars().all()
        return [self._model_to_domain(usr) for usr in db_usrs]

    async def get_service_users(self, service_id: int, role_id: Optional[int] = None, active_only: bool = True) -> List[UserServiceRole]:
        stmt = select(UserServiceRoleModel).where(UserServiceRoleModel.service_id == service_id)
        if role_id:
            stmt = stmt.where(UserServiceRoleModel.role_id == role_id)
        if active_only:
            stmt = stmt.where(UserServiceRoleModel.is_active == True)
        result = await self.session.execute(stmt)
        db_usrs = result.scalars().all()
        return [self._model_to_domain(usr) for usr in db_usrs]

    async def user_has_role_in_service(self, user_id: int, service_id: int, role_id: int) -> bool:
        stmt = select(UserServiceRoleModel).where(
            and_(
                UserServiceRoleModel.user_id == user_id,
                UserServiceRoleModel.service_id == service_id,
                UserServiceRoleModel.role_id == role_id,
                UserServiceRoleModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_role_in_service(self, user_id: int, service_id: int) -> Optional[UserServiceRole]:
        """Get the single role a user has in a specific service"""
        stmt = select(UserServiceRoleModel).where(
            and_(
                UserServiceRoleModel.user_id == user_id,
                UserServiceRoleModel.service_id == service_id,
                UserServiceRoleModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        db_usr = result.scalar_one_or_none()
        return self._model_to_domain(db_usr) if db_usr else None

    async def update_user_role_in_service(self, user_id: int, service_id: int, new_role_id: int) -> UserServiceRole:
        """Update user's role in a specific service (enforces one role per service)"""
        stmt = (
            update(UserServiceRoleModel)
            .where(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id
                )
            )
            .values(role_id=new_role_id)
            .returning(UserServiceRoleModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        db_usr = result.scalar_one()
        return self._model_to_domain(db_usr)

    async def update(self, user_service_role: UserServiceRole) -> UserServiceRole:
        stmt = (
            update(UserServiceRoleModel)
            .where(UserServiceRoleModel.id == user_service_role.id)
            .values(
                user_id=user_service_role.user_id,
                service_id=user_service_role.service_id,
                role_id=user_service_role.role_id,
                is_active=user_service_role.is_active
            )
            .returning(UserServiceRoleModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        db_usr = result.scalar_one()
        return self._model_to_domain(db_usr)
    
    async def delete(self, id: int) -> bool:
        stmt = delete(UserServiceRoleModel).where(UserServiceRoleModel.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def deactivate_user_service_role(self, user_id: int, service_id: int) -> bool:
        """Deactivate user's role in a specific service"""
        stmt = (
            update(UserServiceRoleModel)
            .where(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id
                )
            )
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    def _model_to_domain(self, db_usr: UserServiceRoleModel) -> UserServiceRole:
        return UserServiceRole(
            id=db_usr.id,
            user_id=db_usr.user_id,
            service_id=db_usr.service_id,
            role_id=db_usr.role_id,
            is_active=db_usr.is_active,
            created_at=db_usr.created_at,
            updated_at=db_usr.updated_at
        )