from fastapi import APIRouter, Depends, HTTPException, status

from domain.models.user import User
from interfaces.schemas.user_schemas import UserResponse, UserUpdateRequest
from interfaces.dependencies import (
    get_current_user, get_user_repository, get_user_service_role_repository
)
from domain.repositories.user_repository import UserRepository
from domain.repositories.user_service_role_repository import UserServiceRoleRepository

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get current user information with roles"""
    # Use SQLAlchemy relationships to get user with populated roles
    db_user_with_roles = await user_repo.get_by_id_with_roles(current_user.id)
    result = user_repo.db_user_to_response_dict(db_user_with_roles)
    
    return UserResponse(
        id=result['user'].id,
        phone_number=result['user'].phone_number,
        full_name=result['user'].full_name,
        email=result['user'].email,
        is_active=result['user'].is_active,
        is_verified=result['user'].is_verified,
        mfa_enabled=result['user'].mfa_enabled,
        created_at=result['user'].created_at,
        last_login=result['user'].last_login,
        roles=result['roles']
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Update current user information"""
    # Check if user is trying to update role_id - only admin can do this
    if user_update.role_id is not None:
        # Check if current user has admin role in userService (service_id=1)
        is_admin = await user_service_role_repo.user_has_role_in_service(
            user_id=current_user.id, 
            service_id=1, 
            role_id=1  # Admin role
        )
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can update user roles"
            )
    
    # Update user fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.email is not None:
        current_user.email = user_update.email
    
    try:
        updated_user = await user_repo.update(current_user)
        
        # Handle role update if provided
        if user_update.role_id is not None:
            # For simplicity, update the user's role in userService
            # In a real scenario, you might want to be more specific about which service
            user_roles = await user_service_role_repo.get_user_roles_in_service(
                user_id=current_user.id, 
                service_id=1  # userService
            )
            
            # Deactivate existing roles and create new one
            for role in user_roles:
                await user_service_role_repo.deactivate_user_service_role(
                    user_id=current_user.id,
                    service_id=1,
                    role_id=role.role_id
                )
            
            # Create new role assignment
            from domain.models.user_service_role import UserServiceRole
            new_role = UserServiceRole(
                id=None,
                user_id=current_user.id,
                service_id=1,
                role_id=user_update.role_id,
                is_active=True
            )
            await user_service_role_repo.create(new_role)
        
        # Use SQLAlchemy relationships to get updated user with populated roles
        db_user_with_roles = await user_repo.get_by_id_with_roles(updated_user.id)
        result = user_repo.db_user_to_response_dict(db_user_with_roles)
        
        return UserResponse(
            id=result['user'].id,
            phone_number=result['user'].phone_number,
            full_name=result['user'].full_name,
            email=result['user'].email,
            is_active=result['user'].is_active,
            is_verified=result['user'].is_verified,
            mfa_enabled=result['user'].mfa_enabled,
            created_at=result['user'].created_at,
            last_login=result['user'].last_login,
            roles=result['roles']
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))