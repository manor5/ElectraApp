from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from domain.models.user_role import UserRole
from domain.repositories.user_role_repository import UserRoleRepository
from infrastructure.db.models.user_role import UserRoleModel
from .base_repository import BaseRepository


class UserRoleRepositoryImpl(BaseRepository[UserRole, UserRoleModel], UserRoleRepository):
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def create(self, user_role: UserRole) -> UserRole:
        db_role = self._to_database(user_role)
        db_role = self._commit_and_refresh(db_role)
        return self._to_domain(db_role)
    
    async def get_by_id(self, role_id: int) -> Optional[UserRole]:
        db_role = self.db.query(UserRoleModel).filter(UserRoleModel.id == role_id).first()
        return self._to_domain(db_role) if db_role else None
    
    async def get_by_name(self, name: str) -> Optional[UserRole]:
        db_role = self.db.query(UserRoleModel).filter(UserRoleModel.name == name).first()
        return self._to_domain(db_role) if db_role else None
    
    async def get_all(self, active_only: bool = True) -> List[UserRole]:
        query = self.db.query(UserRoleModel)
        if active_only:
            query = query.filter(UserRoleModel.is_active == True)
        db_roles = query.all()
        return [self._to_domain(role) for role in db_roles]
    
    async def update(self, user_role: UserRole) -> UserRole:
        db_role = self.db.query(UserRoleModel).filter(UserRoleModel.id == user_role.id).first()
        if db_role:
            db_role.name = user_role.name
            db_role.description = user_role.description
            db_role.is_active = user_role.is_active
            if self._safe_commit():
                return self._to_domain(db_role)
        raise ValueError("Role not found or update failed")
    
    async def delete(self, role_id: int) -> bool:
        db_role = self.db.query(UserRoleModel).filter(UserRoleModel.id == role_id).first()
        if db_role:
            self.db.delete(db_role)
            return self._safe_commit()
        return False
    
    def _to_domain(self, db_role: UserRoleModel) -> UserRole:
        """Convert database model to domain model"""
        return UserRole(
            id=db_role.id,
            name=db_role.name,
            description=db_role.description,
            is_active=db_role.is_active,
            created_at=db_role.created_at,
            updated_at=db_role.updated_at
        )
    
    def _to_database(self, user_role: UserRole) -> UserRoleModel:
        """Convert domain model to database model"""
        return UserRoleModel(
            id=user_role.id,
            name=user_role.name,
            description=user_role.description,
            is_active=user_role.is_active,
            created_at=user_role.created_at,
            updated_at=user_role.updated_at
        )