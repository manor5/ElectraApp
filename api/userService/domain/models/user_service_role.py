from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserServiceRole:
    id: Optional[int]
    user_id: int
    service_id: int
    role_id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None