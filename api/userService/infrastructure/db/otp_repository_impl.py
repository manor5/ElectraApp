from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from domain.models.user import OTPVerification
from domain.repositories.user_repository import OTPRepository
from .models import OTPVerificationModel
from .base_repository import BaseRepository


class SQLOTPRepository(BaseRepository[OTPVerification, OTPVerificationModel], OTPRepository):
    """SQL implementation of OTPRepository interface"""
    
    def __init__(self, db: Session):
        super().__init__(db)

    async def create(self, otp: OTPVerification) -> OTPVerification:
        """Create a new OTP verification record"""
        db_otp = self._to_database(otp)
        db_otp = self._commit_and_refresh(db_otp)
        return self._to_domain(db_otp)

    async def get_by_phone_and_purpose(self, phone_number: str, purpose: str) -> Optional[OTPVerification]:
        """Retrieve active OTP by phone number and purpose"""
        db_otp = self.db.query(OTPVerificationModel).filter(
            and_(
                OTPVerificationModel.phone_number == phone_number,
                OTPVerificationModel.purpose == purpose,
                OTPVerificationModel.is_used == False
            )
        ).first()
        
        return self._to_domain(db_otp) if db_otp else None

    async def mark_as_used(self, otp_id: int) -> bool:
        """Mark an OTP as used"""
        db_otp = self.db.query(OTPVerificationModel).filter(OTPVerificationModel.id == otp_id).first()
        if db_otp:
            db_otp.is_used = True
            return self._safe_commit()
        return False

    async def cleanup_expired(self) -> int:
        """Remove expired OTP records and return count of removed records"""
        expired_count = self.db.query(OTPVerificationModel).filter(
            OTPVerificationModel.expires_at < datetime.utcnow()
        ).count()
        
        self.db.query(OTPVerificationModel).filter(
            OTPVerificationModel.expires_at < datetime.utcnow()
        ).delete()
        
        return expired_count if self._safe_commit() else 0

    def _to_domain(self, db_otp: OTPVerificationModel) -> OTPVerification:
        """Convert database model to domain model"""
        return OTPVerification(
            id=db_otp.id,
            phone_number=db_otp.phone_number,
            otp_code=db_otp.otp_code,
            purpose=db_otp.purpose,
            is_used=db_otp.is_used,
            expires_at=db_otp.expires_at,
            created_at=db_otp.created_at
        )

    def _to_database(self, otp: OTPVerification) -> OTPVerificationModel:
        """Convert domain model to database model"""
        return OTPVerificationModel(
            id=otp.id,
            phone_number=otp.phone_number,
            otp_code=otp.otp_code,
            purpose=otp.purpose,
            is_used=otp.is_used,
            expires_at=otp.expires_at,
            created_at=otp.created_at
        )