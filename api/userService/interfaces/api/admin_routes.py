from fastapi import APIRouter, Depends, HTTPException, status

from domain.models.user import User
from interfaces.schemas.user_schemas import UserResponse, MessageResponse
from interfaces.dependencies import get_current_user, get_user_repository
from domain.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/users")
async def list_users(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """List all users (admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await user_repo.list_all()
    return [
        UserResponse(
            id=user.id,
            phone_number=user.phone_number,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
            last_login=user.last_login
        ) for user in users
    ]

@router.put("/users/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Deactivate a user (admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        await user_repo.update(user)
        
        return MessageResponse(message=f"User {user.phone_number} deactivated successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))