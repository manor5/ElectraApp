"""
Central repository module for backward compatibility and easy imports.
This module re-exports all repository implementations.
"""

# Import all repository implementations
from .user_repository_impl import SQLUserRepository
from .otp_repository_impl import SQLOTPRepository
from .base_repository import BaseRepository

# Re-export for backward compatibility
__all__ = [
    'SQLUserRepository',
    'SQLOTPRepository', 
    'BaseRepository'
]