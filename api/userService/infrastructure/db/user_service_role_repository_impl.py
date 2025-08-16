from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import joinedload
from domain.models.user_service_role import UserServiceRole
from domain.repositories.user_service_role_repository import UserServiceRoleRepository
from infrastructure.db.models.user_service_role import UserServiceRoleModel
from .base_repository import BaseRepository


class UserServiceRoleRepositoryImpl(BaseRepository[UserServiceRole, UserServiceRoleModel], UserServiceRoleRepository):
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def create(self, user_service_role: UserServiceRole) -> UserServiceRole:
        db_usr = self._to_database(user_service_role)
        db_usr = self._commit_and_refresh(db_usr)
        return self._to_domain(db_usr)
    
    async def get_by_id(self, id: int) -> Optional[UserServiceRole]:
        db_usr = self.db.query(UserServiceRoleModel).filter(UserServiceRoleModel.id == id).first()
        return self._to_domain(db_usr) if db_usr else None

    async def get_user_roles_in_service(self, user_id: int, service_id: int) -> List[UserServiceRole]:
        db_usrs = (
            self.db.query(UserServiceRoleModel)
            .filter(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id,
                    UserServiceRoleModel.is_active == True
                )
            )
            .all()
        )
        return [self._to_domain(usr) for usr in db_usrs]

    async def get_user_services(self, user_id: int, active_only: bool = True) -> List[UserServiceRole]:
        query = self.db.query(UserServiceRoleModel).filter(UserServiceRoleModel.user_id == user_id)
        if active_only:
            query = query.filter(UserServiceRoleModel.is_active == True)
        db_usrs = query.all()
        return [self._to_domain(usr) for usr in db_usrs]

    async def get_service_users(self, service_id: int, role_id: Optional[int] = None, active_only: bool = True) -> List[UserServiceRole]:
        query = self.db.query(UserServiceRoleModel).filter(UserServiceRoleModel.service_id == service_id)
        if role_id:
            query = query.filter(UserServiceRoleModel.role_id == role_id)
        if active_only:
            query = query.filter(UserServiceRoleModel.is_active == True)
        db_usrs = query.all()
        return [self._to_domain(usr) for usr in db_usrs]

    async def user_has_role_in_service(self, user_id: int, service_id: int, role_id: int) -> bool:
        db_usr = (
            self.db.query(UserServiceRoleModel)
            .filter(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id,
                    UserServiceRoleModel.role_id == role_id,
                    UserServiceRoleModel.is_active == True
                )
            )
            .first()
        )
        return db_usr is not None

    async def get_user_role_in_service(self, user_id: int, service_id: int) -> Optional[UserServiceRole]:
        """Get the single role a user has in a specific service"""
        db_usr = (
            self.db.query(UserServiceRoleModel)
            .filter(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id,
                    UserServiceRoleModel.is_active == True
                )
            )
            .first()
        )
        return self._to_domain(db_usr) if db_usr else None

    async def update_user_role_in_service(self, user_id: int, service_id: int, new_role_id: int) -> UserServiceRole:
        """Update user's role in a specific service (enforces one role per service)"""
        db_usr = (
            self.db.query(UserServiceRoleModel)
            .filter(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id
                )
            )
            .first()
        )
        if db_usr:
            db_usr.role_id = new_role_id
            if self._safe_commit():
                return self._to_domain(db_usr)
        raise ValueError("User service role not found or update failed")

    async def update(self, user_service_role: UserServiceRole) -> UserServiceRole:
        db_usr = self.db.query(UserServiceRoleModel).filter(UserServiceRoleModel.id == user_service_role.id).first()
        if db_usr:
            db_usr.user_id = user_service_role.user_id
            db_usr.service_id = user_service_role.service_id
            db_usr.role_id = user_service_role.role_id
            db_usr.is_active = user_service_role.is_active
            if self._safe_commit():
                return self._to_domain(db_usr)
        raise ValueError("User service role not found or update failed")
    
    async def delete(self, id: int) -> bool:
        db_usr = self.db.query(UserServiceRoleModel).filter(UserServiceRoleModel.id == id).first()
        if db_usr:
            self.db.delete(db_usr)
            return self._safe_commit()
        return False

    async def deactivate_user_service_role(self, user_id: int, service_id: int) -> bool:
        """Deactivate user's role in a specific service"""
        db_usr = (
            self.db.query(UserServiceRoleModel)
            .filter(
                and_(
                    UserServiceRoleModel.user_id == user_id,
                    UserServiceRoleModel.service_id == service_id
                )
            )
            .first()
        )
        if db_usr:
            db_usr.is_active = False
            return self._safe_commit()
        return False
    
    def _to_domain(self, db_usr: UserServiceRoleModel) -> UserServiceRole:
        """Convert database model to domain model"""
        return UserServiceRole(
            id=db_usr.id,
            user_id=db_usr.user_id,
            service_id=db_usr.service_id,
            role_id=db_usr.role_id,
            is_active=db_usr.is_active,
            created_at=db_usr.created_at,
            updated_at=db_usr.updated_at
        )
    
    def _to_database(self, user_service_role: UserServiceRole) -> UserServiceRoleModel:
        """Convert domain model to database model"""
        return UserServiceRoleModel(
            id=user_service_role.id,
            user_id=user_service_role.user_id,
            service_id=user_service_role.service_id,
            role_id=user_service_role.role_id,
            is_active=user_service_role.is_active,
            created_at=user_service_role.created_at,
            updated_at=user_service_role.updated_at
        )