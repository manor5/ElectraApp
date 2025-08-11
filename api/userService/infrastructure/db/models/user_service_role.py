from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class UserServiceRoleModel(Base):
    __tablename__ = "user_service_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint: one role per user per service
    __table_args__ = (UniqueConstraint('user_id', 'service_id', name='uq_user_service'),)
    
    # Relationships
    user = relationship("UserModel", back_populates="user_service_roles")
    service = relationship("ServiceModel", back_populates="user_service_roles")
    role = relationship("UserRoleModel", back_populates="user_service_roles")