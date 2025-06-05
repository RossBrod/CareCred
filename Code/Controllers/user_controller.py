from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Models.user import BaseUser, Student, Senior, Admin, UserType
from ..Services.authentication_service import AuthenticationService
from .schemas import (
    UserProfileUpdate, StudentProfileUpdate, SeniorProfileUpdate,
    PaginatedResponse, UserResponse, APIResponse
)
from .dependencies import (
    AuthDependencies, ValidationDependencies, get_current_user,
    get_current_student_user, get_current_senior_user, get_current_admin_user,
    get_pagination
)


router = APIRouter()

def get_auth_service() -> AuthenticationService:
    return AuthenticationService()


@router.get("/me",
           response_model=UserResponse,
           summary="Get current user profile",
           description="Get detailed profile information for the current authenticated user")
async def get_current_user_profile(
    current_user: BaseUser = Depends(get_current_user)
):
    """Get current user's detailed profile."""
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        user_type=current_user.get_user_type(),
        status=current_user.status,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        rating=getattr(current_user, 'rating', 0.0),
        total_reviews=getattr(current_user, 'total_reviews', 0)
    )


@router.put("/me",
           response_model=APIResponse,
           summary="Update current user profile",
           description="Update profile information for the current authenticated user")
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Update current user's profile."""
    try:
        success = await auth_service.update_user_profile(
            current_user.user_id,
            profile_data.dict(exclude_unset=True)
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Profile updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.put("/me/student",
           response_model=APIResponse,
           summary="Update student profile",
           description="Update student-specific profile information")
async def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_student: Student = Depends(get_current_student_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Update student-specific profile data."""
    try:
        success = await auth_service.update_student_profile(
            current_student.user_id,
            profile_data.dict(exclude_unset=True)
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Student profile updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update student profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student profile update failed"
        )


@router.put("/me/senior",
           response_model=APIResponse,
           summary="Update senior profile",
           description="Update senior-specific profile information")
async def update_senior_profile(
    profile_data: SeniorProfileUpdate,
    current_senior: Senior = Depends(get_current_senior_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Update senior-specific profile data."""
    try:
        success = await auth_service.update_senior_profile(
            current_senior.user_id,
            profile_data.dict(exclude_unset=True)
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Senior profile updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update senior profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Senior profile update failed"
        )


@router.post("/me/avatar",
            response_model=APIResponse,
            summary="Upload profile photo",
            description="Upload and set profile photo for current user")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Upload and set profile photo."""
    try:
        # Validate file type and size
        if not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        if photo.size > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size cannot exceed 5MB"
            )
        
        # Process and store photo
        photo_url = await auth_service.upload_profile_photo(
            current_user.user_id,
            photo
        )
        
        return APIResponse(
            success=True,
            message=f"Profile photo uploaded successfully. URL: {photo_url}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Photo upload failed"
        )


@router.get("/{user_id}",
           response_model=UserResponse,
           summary="Get user by ID",
           description="Get public profile information for a specific user")
async def get_user_by_id(
    user_id: str,
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get user profile by ID (with privacy controls)."""
    try:
        # Check if user can view this profile
        can_view = await auth_service.can_view_user_profile(
            current_user.user_id,
            user_id
        )
        
        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to user profile"
            )
        
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email if current_user.get_user_type() == UserType.ADMIN else None,
            first_name=user.first_name,
            last_name=user.last_name,
            user_type=user.get_user_type(),
            status=user.status,
            created_at=user.created_at,
            last_login=None,  # Privacy: don't expose last login
            rating=getattr(user, 'rating', 0.0),
            total_reviews=getattr(user, 'total_reviews', 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.get("/search/students",
           response_model=PaginatedResponse,
           summary="Search students",
           description="Search and filter students (for seniors and admins)")
async def search_students(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    university: Optional[str] = Query(None, description="Filter by university"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    has_transportation: Optional[bool] = Query(None, description="Filter by transportation"),
    max_distance: Optional[float] = Query(None, description="Maximum travel distance"),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Search students with filters."""
    try:
        # Only seniors and admins can search students
        if current_user.get_user_type() not in [UserType.SENIOR, UserType.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Build search filters
        filters = {}
        if university:
            filters['university'] = university
        if skills:
            filters['skills'] = skills.split(',')
        if has_transportation is not None:
            filters['has_transportation'] = has_transportation
        if max_distance is not None:
            filters['max_travel_distance'] = max_distance
        
        # Search students
        result = await auth_service.search_students(
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.students,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student search failed"
        )


@router.get("/search/seniors",
           response_model=PaginatedResponse,
           summary="Search seniors",
           description="Search and filter seniors (for students and admins)")
async def search_seniors(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    city: Optional[str] = Query(None, description="Filter by city"),
    help_needed: Optional[str] = Query(None, description="Comma-separated help types"),
    max_distance_from: Optional[str] = Query(None, description="Distance from address"),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Search seniors with filters."""
    try:
        # Only students and admins can search seniors
        if current_user.get_user_type() not in [UserType.STUDENT, UserType.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Build search filters
        filters = {}
        if city:
            filters['city'] = city
        if help_needed:
            filters['help_needed'] = help_needed.split(',')
        if max_distance_from:
            filters['max_distance_from'] = max_distance_from
        
        # Search seniors
        result = await auth_service.search_seniors(
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.seniors,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Senior search failed"
        )


@router.delete("/me",
              response_model=APIResponse,
              summary="Delete user account",
              description="Permanently delete current user account")
async def delete_current_user_account(
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Delete current user's account."""
    try:
        success = await auth_service.delete_user_account(current_user.user_id)
        
        if success:
            return APIResponse(
                success=True,
                message="Account deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete account"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.post("/me/deactivate",
            response_model=APIResponse,
            summary="Deactivate user account",
            description="Temporarily deactivate current user account")
async def deactivate_current_user_account(
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Deactivate current user's account."""
    try:
        success = await auth_service.deactivate_user_account(current_user.user_id)
        
        if success:
            return APIResponse(
                success=True,
                message="Account deactivated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate account"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )


# Export the router
user_router = router