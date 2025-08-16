from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from domain.models.user import User
from domain.models.service import Service
from domain.models.user_role import UserRole
from domain.models.user_service_role import UserServiceRole
from interfaces.schemas.user_schemas import (
    UserResponse, MessageResponse, ServiceResponse, UserRoleResponse, 
    UserServiceRoleResponse, ServiceCreateRequest, ServiceUpdateRequest,
    UserRoleCreateRequest, UserRoleUpdateRequest, UserServiceRoleCreateRequest,
    UserServiceRoleUpdateRequest
)
from interfaces.dependencies import (
    get_current_user, get_user_repository, get_service_repository,
    get_user_role_repository, get_user_service_role_repository
)
from domain.repositories.user_repository import UserRepository
from domain.repositories.service_repository import ServiceRepository
from domain.repositories.user_role_repository import UserRoleRepository
from domain.repositories.user_service_role_repository import UserServiceRoleRepository

router = APIRouter(prefix="/admin", tags=["Administration"])

async def check_admin_access(
    current_user: User, 
    user_service_role_repo: UserServiceRoleRepository
):
    """Helper function to check admin access using new role system"""
    # Get userService (assuming ID 1 for userService)
    # In production, you'd want to get this by name
    user_service_roles = await user_service_role_repo.get_user_services(current_user.id)
    
    # Check if user has admin role in userService
    has_admin_role = False
    for usr in user_service_roles:
        if usr.service_id == 1 and usr.role_id == 1:  # Assuming admin role has ID 1
            has_admin_role = True
            break
    
    if not has_admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

# User management endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """List all users (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    # Get users with their roles
    users = await user_repo.list_all()
    user_responses = []
    
    for user in users:
        db_user_with_roles = await user_repo.get_by_id_with_roles(user.id)
        result = user_repo.db_user_to_response_dict(db_user_with_roles)
        
        user_responses.append(UserResponse(
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
        ))
    
    return user_responses

@router.put("/users/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Deactivate a user (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
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

# Service management endpoints
@router.get("/services", response_model=List[ServiceResponse])
async def list_services(
    current_user: User = Depends(get_current_user),
    service_repo: ServiceRepository = Depends(get_service_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """List all services (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    services = await service_repo.get_all(active_only=False)
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description
        ) for service in services
    ]

@router.post("/services", response_model=ServiceResponse)
async def create_service(
    service_request: ServiceCreateRequest,
    current_user: User = Depends(get_current_user),
    service_repo: ServiceRepository = Depends(get_service_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Create a new service (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        # Check if service already exists
        existing_service = await service_repo.get_by_name(service_request.name)
        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service with this name already exists"
            )
        
        service = Service(
            name=service_request.name,
            description=service_request.description,
            is_active=True
        )
        
        created_service = await service_repo.create(service)
        return ServiceResponse(
            id=created_service.id,
            name=created_service.name,
            description=created_service.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    service_repo: ServiceRepository = Depends(get_service_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Get a specific service (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description
    )

@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_request: ServiceUpdateRequest,
    current_user: User = Depends(get_current_user),
    service_repo: ServiceRepository = Depends(get_service_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Update a service (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        service = await service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Update only provided fields
        if service_request.name is not None:
            service.name = service_request.name
        if service_request.description is not None:
            service.description = service_request.description
        if service_request.is_active is not None:
            service.is_active = service_request.is_active
        
        updated_service = await service_repo.update(service)
        return ServiceResponse(
            id=updated_service.id,
            name=updated_service.name,
            description=updated_service.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/services/{service_id}", response_model=MessageResponse)
async def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    service_repo: ServiceRepository = Depends(get_service_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Delete a service (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        deleted = await service_repo.delete(service_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        return MessageResponse(message="Service deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Role management endpoints
@router.get("/roles", response_model=List[UserRoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
    role_repo: UserRoleRepository = Depends(get_user_role_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """List all roles (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    roles = await role_repo.get_all(active_only=False)
    return [
        UserRoleResponse(
            id=role.id,
            name=role.name,
            description=role.description
        ) for role in roles
    ]

@router.post("/roles", response_model=UserRoleResponse)
async def create_role(
    role_request: UserRoleCreateRequest,
    current_user: User = Depends(get_current_user),
    role_repo: UserRoleRepository = Depends(get_user_role_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Create a new role (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        # Check if role already exists
        existing_role = await role_repo.get_by_name(role_request.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        role = UserRole(
            name=role_request.name,
            description=role_request.description,
            is_active=True
        )
        
        created_role = await role_repo.create(role)
        return UserRoleResponse(
            id=created_role.id,
            name=created_role.name,
            description=created_role.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/roles/{role_id}", response_model=UserRoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_repo: UserRoleRepository = Depends(get_user_role_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Get a specific role (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    role = await role_repo.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return UserRoleResponse(
        id=role.id,
        name=role.name,
        description=role.description
    )

@router.put("/roles/{role_id}", response_model=UserRoleResponse)
async def update_role(
    role_id: int,
    role_request: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    role_repo: UserRoleRepository = Depends(get_user_role_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Update a role (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        role = await role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Update only provided fields
        if role_request.name is not None:
            role.name = role_request.name
        if role_request.description is not None:
            role.description = role_request.description
        if role_request.is_active is not None:
            role.is_active = role_request.is_active
        
        updated_role = await role_repo.update(role)
        return UserRoleResponse(
            id=updated_role.id,
            name=updated_role.name,
            description=updated_role.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/roles/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_repo: UserRoleRepository = Depends(get_user_role_repository),
    user_service_role_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Delete a role (admin only)"""
    await check_admin_access(current_user, user_service_role_repo)
    
    try:
        deleted = await role_repo.delete(role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return MessageResponse(message="Role deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Service Role management endpoints
@router.get("/service-roles", response_model=List[UserServiceRoleResponse])
async def list_service_roles(
    service_id: int = Query(None),
    user_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    usr_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """List service roles with optional filtering (admin only)"""
    await check_admin_access(current_user, usr_repo)
    
    try:
        if user_id and service_id:
            # Get specific user role in service
            user_service_role = await usr_repo.get_user_role_in_service(user_id, service_id)
            return [user_service_role] if user_service_role else []
        elif user_id:
            # Get all services for a user
            user_services = await usr_repo.get_user_services(user_id, active_only=False)
            return user_services
        elif service_id:
            # Get all users in a service
            service_users = await usr_repo.get_service_users(service_id, active_only=False)
            return service_users
        else:
            # This would require a new method to get all service roles
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide either user_id or service_id as query parameter"
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/service-roles", response_model=UserServiceRoleResponse)
async def create_service_role(
    usr_request: UserServiceRoleCreateRequest,
    current_user: User = Depends(get_current_user),
    usr_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Create a new user service role (admin only)"""
    await check_admin_access(current_user, usr_repo)
    
    try:
        # Check if user already has a role in this service
        existing_role = await usr_repo.get_user_role_in_service(
            usr_request.user_id, usr_request.service_id
        )
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a role in this service. Use update instead."
            )
        
        user_service_role = UserServiceRole(
            user_id=usr_request.user_id,
            service_id=usr_request.service_id,
            role_id=usr_request.role_id,
            is_active=True
        )
        
        created_usr = await usr_repo.create(user_service_role)
        return created_usr
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/service-roles/{usr_id}", response_model=UserServiceRoleResponse)
async def get_service_role(
    usr_id: int,
    current_user: User = Depends(get_current_user),
    usr_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Get a specific service role (admin only)"""
    await check_admin_access(current_user, usr_repo)
    
    usr = await usr_repo.get_by_id(usr_id)
    if not usr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service role not found"
        )
    
    return usr

@router.put("/service-roles/{usr_id}", response_model=UserServiceRoleResponse)
async def update_service_role(
    usr_id: int,
    usr_request: UserServiceRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    usr_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Update a service role (admin only)"""
    await check_admin_access(current_user, usr_repo)
    
    try:
        usr = await usr_repo.get_by_id(usr_id)
        if not usr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service role not found"
            )
        
        # Update only provided fields
        if usr_request.user_id is not None:
            usr.user_id = usr_request.user_id
        if usr_request.service_id is not None:
            usr.service_id = usr_request.service_id
        if usr_request.role_id is not None:
            usr.role_id = usr_request.role_id
        if usr_request.is_active is not None:
            usr.is_active = usr_request.is_active
        
        updated_usr = await usr_repo.update(usr)
        return updated_usr
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/service-roles/{usr_id}", response_model=MessageResponse)
async def delete_service_role(
    usr_id: int,
    current_user: User = Depends(get_current_user),
    usr_repo: UserServiceRoleRepository = Depends(get_user_service_role_repository)
):
    """Delete a service role (admin only)"""
    await check_admin_access(current_user, usr_repo)
    
    try:
        deleted = await usr_repo.delete(usr_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service role not found"
            )
        
        return MessageResponse(message="Service role deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))