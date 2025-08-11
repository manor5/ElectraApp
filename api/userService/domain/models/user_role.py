from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserRole:
    id: Optional[int]
    name: str  # "admin", "user", "manager", "moderator"
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None