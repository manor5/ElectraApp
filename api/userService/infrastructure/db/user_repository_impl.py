import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from .models import UserModel
from .models.user_service_role import UserServiceRoleModel
from .base_repository import BaseRepository


class SQLUserRepository(BaseRepository[User, UserModel], UserRepository):
    """SQL implementation of UserRepository interface"""
    
    def __init__(self, db: Session):
        super().__init__(db)

    async def create(self, user: User) -> User:
        """Create a new user in the database"""
        db_user = self._to_database(user)
        db_user = self._commit_and_refresh(db_user)
        return self._to_domain(db_user)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_domain(db_user) if db_user else None

    async def get_by_id_with_roles(self, user_id: int) -> Optional[UserModel]:
        """Retrieve user by ID with service roles eagerly loaded"""
        db_user = (
            self.db.query(UserModel)
            .options(
                joinedload(UserModel.user_service_roles)
                .joinedload(UserServiceRoleModel.role),
                joinedload(UserModel.user_service_roles)
                .joinedload(UserServiceRoleModel.service)
            )
            .filter(UserModel.id == user_id)
            .first()
        )
        return db_user

    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Retrieve user by phone number"""
        db_user = self.db.query(UserModel).filter(UserModel.phone_number == phone_number).first()
        return self._to_domain(db_user) if db_user else None

    async def get_by_phone_number_with_roles(self, phone_number: str) -> Optional[UserModel]:
        """Retrieve user by phone number with service roles eagerly loaded"""
        db_user = (
            self.db.query(UserModel)
            .options(
                joinedload(UserModel.user_service_roles)
                .joinedload(UserServiceRoleModel.role),
                joinedload(UserModel.user_service_roles)
                .joinedload(UserServiceRoleModel.service)
            )
            .filter(UserModel.phone_number == phone_number)
            .first()
        )
        return db_user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_domain(db_user) if db_user else None

    async def update(self, user: User) -> User:
        """Update an existing user"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            raise ValueError(f"User with id {user.id} not found")

        # Update fields
        db_user.phone_number = user.phone_number
        db_user.full_name = user.full_name
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        db_user.is_verified = user.is_verified
        db_user.mfa_enabled = user.mfa_enabled
        db_user.mfa_secret = user.mfa_secret
        db_user.backup_codes = json.dumps(user.backup_codes) if user.backup_codes else None
        db_user.last_login = user.last_login
        db_user.updated_at = datetime.utcnow()

        if self._safe_commit():
            self.db.refresh(db_user)
            return self._to_domain(db_user)
        else:
            raise RuntimeError("Failed to update user")

    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            return self._safe_commit()
        return False

    async def list_all(self) -> List[User]:
        """Retrieve all users"""
        db_users = self.db.query(UserModel).all()
        return [self._to_domain(db_user) for db_user in db_users]

    def _to_domain(self, db_user: UserModel) -> User:
        """Convert database model to domain model"""
        backup_codes = json.loads(db_user.backup_codes) if db_user.backup_codes else None
        return User(
            id=db_user.id,
            phone_number=db_user.phone_number,
            full_name=db_user.full_name,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            mfa_enabled=db_user.mfa_enabled,
            mfa_secret=db_user.mfa_secret,
            backup_codes=backup_codes,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )

    def _to_database(self, user: User) -> UserModel:
        """Convert domain model to database model"""
        return UserModel(
            id=user.id,
            phone_number=user.phone_number,
            full_name=user.full_name,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            mfa_secret=user.mfa_secret,
            backup_codes=json.dumps(user.backup_codes) if user.backup_codes else None,
            last_login=user.last_login
        )

    def db_user_to_response_dict(self, db_user: UserModel) -> dict:
        """Convert database user with relationships to response dictionary"""
        backup_codes = json.loads(db_user.backup_codes) if db_user.backup_codes else None
        
        # Convert user service roles to response format (multiple roles across services)
        roles = []
        for user_service_role in db_user.user_service_roles:
            if user_service_role.is_active:  # Only include active roles
                roles.append({
                    'id': user_service_role.id,
                    'service': {
                        'id': user_service_role.service.id,
                        'name': user_service_role.service.name,
                        'description': user_service_role.service.description
                    },
                    'role': {
                        'id': user_service_role.role.id,
                        'name': user_service_role.role.name,
                        'description': user_service_role.role.description
                    },
                    'is_active': user_service_role.is_active,
                    'created_at': user_service_role.created_at
                })
        
        return {
            'user': User(
                id=db_user.id,
                phone_number=db_user.phone_number,
                full_name=db_user.full_name,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_verified=db_user.is_verified,
                mfa_enabled=db_user.mfa_enabled,
                mfa_secret=db_user.mfa_secret,
                backup_codes=backup_codes,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
                last_login=db_user.last_login
            ),
            'roles': roles  # Array of roles across multiple services
        }