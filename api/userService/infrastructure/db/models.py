# This file is kept for backward compatibility
# All models have been moved to the models/ directory
from .models import (
    UserModel, 
    OTPVerificationModel, 
    UserRoleModel, 
    ServiceModel, 
    UserServiceRoleModel
)

__all__ = [
    "UserModel", 
    "OTPVerificationModel", 
    "UserRoleModel", 
    "ServiceModel", 
    "UserServiceRoleModel"
]