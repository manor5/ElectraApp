from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PhoneService:
    """Service responsible for phone/SMS communication operations."""
    
    @staticmethod
    def send_otp(phone_number: str, otp_code: str) -> bool:
        """Send OTP via SMS to the specified phone number."""
        try:
            # In a real application, integrate with SMS service (Twilio, AWS SNS, etc.)
            # For development, we'll just print the OTP
            print(f"📱 SMS to {phone_number}: Your OTP is {otp_code}")
            logger.info(f"OTP sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_notification(phone_number: str, message: str) -> bool:
        """Send a general notification message via SMS."""
        try:
            # For development purposes
            print(f"📱 SMS to {phone_number}: {message}")
            logger.info(f"Notification sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {phone_number}: {str(e)}")
            return False