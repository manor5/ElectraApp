from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session

# Generic types for domain and database models
DomainModel = TypeVar('DomainModel')
DatabaseModel = TypeVar('DatabaseModel')


class BaseRepository(Generic[DomainModel, DatabaseModel], ABC):
    """Abstract base repository class providing common database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def _to_domain(self, db_model: DatabaseModel) -> DomainModel:
        """Convert database model to domain model"""
        pass
    
    @abstractmethod
    def _to_database(self, domain_model: DomainModel) -> DatabaseModel:
        """Convert domain model to database model"""
        pass
    
    def _commit_and_refresh(self, db_model: DatabaseModel) -> DatabaseModel:
        """Common commit and refresh operation"""
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return db_model
    
    def _safe_commit(self) -> bool:
        """Safely commit changes with error handling"""
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False