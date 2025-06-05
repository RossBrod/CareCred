from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from functools import wraps
import logging

from ..Models.user import BaseUser, Student, Senior, Admin, UserType, AdminRole
from ..Services.authentication_service import AuthenticationService, AuthorizationService

# Security scheme
security = HTTPBearer()

# Service instances - these would be properly injected in a real application
def get_auth_service() -> AuthenticationService:
    return AuthenticationService()

def get_authorization_service() -> AuthorizationService:
    return AuthorizationService()

# Initialize services
auth_service = get_auth_service()
authorization_service = get_authorization_service()

class AuthDependencies:
    """Authentication and authorization dependencies"""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> BaseUser:
        """Get current authenticated user from JWT token"""
        try:
            if not auth_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service not available"
                )
            
            user = auth_service.validate_token(credentials.credentials)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return user
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    async def get_current_active_user(
        current_user: BaseUser = Depends(get_current_user)
    ) -> BaseUser:
        """Get current active user (not suspended/disabled)"""
        if current_user.status.value == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is suspended"
            )
        return current_user
    
    @staticmethod
    async def get_current_student(
        current_user: BaseUser = Depends(get_current_active_user)
    ) -> Student:
        """Get current user as Student, raise error if not a student"""
        if current_user.get_user_type() != UserType.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access required"
            )
        return current_user
    
    @staticmethod
    async def get_current_senior(
        current_user: BaseUser = Depends(get_current_active_user)
    ) -> Senior:
        """Get current user as Senior, raise error if not a senior"""
        if current_user.get_user_type() != UserType.SENIOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Senior access required"
            )
        return current_user
    
    @staticmethod
    async def get_current_admin(
        current_user: BaseUser = Depends(get_current_active_user)
    ) -> Admin:
        """Get current user as Admin, raise error if not an admin"""
        if current_user.get_user_type() != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator access required"
            )
        return current_user
    
    @staticmethod
    async def get_super_admin(
        current_admin: Admin = Depends(get_current_admin)
    ) -> Admin:
        """Get current admin with super admin privileges"""
        if current_admin.admin_role != AdminRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super administrator access required"
            )
        return current_admin

class PermissionDependencies:
    """Permission-based authorization dependencies"""
    
    @staticmethod
    def require_permission(permission: str):
        """Decorator factory for requiring specific permissions"""
        def permission_dependency(
            current_user: BaseUser = Depends(AuthDependencies.get_current_active_user)
        ) -> BaseUser:
            if not authorization_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authorization service not available"
                )
            
            if not authorization_service.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
            return current_user
        
        return permission_dependency
    
    @staticmethod
    def require_admin_permission(permission: str):
        """Decorator factory for requiring specific admin permissions"""
        def admin_permission_dependency(
            current_admin: Admin = Depends(AuthDependencies.get_current_admin)
        ) -> Admin:
            if not authorization_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authorization service not available"
                )
            
            if not authorization_service.require_admin_permission(current_admin, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Admin permission required: {permission}"
                )
            return current_admin
        
        return admin_permission_dependency

class ValidationDependencies:
    """Common validation dependencies"""
    
    @staticmethod
    async def validate_pagination(
        page: int = 1,
        limit: int = 20,
        max_limit: int = 100
    ) -> dict:
        """Validate pagination parameters"""
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1"
            )
        
        if limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be >= 1"
            )
        
        if limit > max_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limit cannot exceed {max_limit}"
            )
        
        offset = (page - 1) * limit
        return {"limit": limit, "offset": offset, "page": page}
    
    @staticmethod
    async def validate_user_access(
        target_user_id: str,
        current_user: BaseUser = Depends(AuthDependencies.get_current_active_user)
    ) -> str:
        """Validate user can access target user's data"""
        # Users can access their own data
        if current_user.user_id == target_user_id:
            return target_user_id
        
        # Admins can access any user's data
        if current_user.get_user_type() == UserType.ADMIN:
            return target_user_id
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to user data"
        )

class RateLimitDependencies:
    """Rate limiting dependencies"""
    
    @staticmethod
    async def rate_limit_check(request: Request) -> None:
        """Check rate limits for the current request"""
        # Implement rate limiting logic here
        # This is a placeholder for actual rate limiting implementation
        client_ip = request.client.host
        # Check rate limit for client_ip
        pass

# Convenience functions for common dependency combinations
def get_current_student_user():
    """Dependency for endpoints requiring student access"""
    return Depends(AuthDependencies.get_current_student)

def get_current_senior_user():
    """Dependency for endpoints requiring senior access"""
    return Depends(AuthDependencies.get_current_senior)

def get_current_admin_user():
    """Dependency for endpoints requiring admin access"""
    return Depends(AuthDependencies.get_current_admin)

def get_pagination():
    """Dependency for pagination parameters"""
    return Depends(ValidationDependencies.validate_pagination)

def require_permissions(*permissions: str):
    """Dependency factory for multiple permission requirements"""
    async def dependency(
        current_user: BaseUser = Depends(AuthDependencies.get_current_active_user)
    ) -> BaseUser:
        if not authorization_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization service not available"
            )
        
        for permission in permissions:
            if not authorization_service.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
        return current_user
    
    return Depends(dependency)

# Export convenience functions for easy import
get_current_user = AuthDependencies.get_current_user