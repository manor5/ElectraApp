import pyotp
import qrcode
import secrets
from io import BytesIO
from base64 import b64encode
from typing import List

from core.config import settings

class MFAService:
    """Service responsible for Multi-Factor Authentication operations."""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a random base32 secret for TOTP."""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(phone_number: str, secret: str) -> str:
        """Generate a QR code for TOTP setup in authenticator apps."""
        totp_uri = pyotp.TOTP(secret).provisioning_uri(
            name=phone_number,
            issuer_name=settings.MFA_ISSUER
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify a TOTP token against a secret."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for MFA recovery."""
        return [secrets.token_hex(4).upper() for _ in range(count)]