from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Services.authentication_service import AuthenticationService, IdentityVerificationService, AuthorizationService
from ..Models.user import UserType, BaseUser
from .schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, PasswordResetRequest,
    PasswordResetConfirm, ChangePasswordRequest, StudentRegistrationRequest,
    SeniorRegistrationRequest, AdminRegistrationRequest, APIResponse
)
from .dependencies import AuthDependencies, get_current_user


router = APIRouter()
security = HTTPBearer()

# Service dependencies - these would be injected in a real application
def get_auth_service() -> AuthenticationService:
    return AuthenticationService()

def get_verification_service() -> IdentityVerificationService:
    return IdentityVerificationService()

def get_authorization_service() -> AuthorizationService:
    return AuthorizationService()


@router.post("/register/student", 
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Register new student",
            description="Register a new student account with university verification")
async def register_student(
    registration_data: StudentRegistrationRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Register new student with email verification."""
    try:
        result = await auth_service.register_student(registration_data.dict())
        
        if result.success:
            # Send verification email in background
            background_tasks.add_task(
                auth_service.send_verification_email,
                result.user_id,
                registration_data.email
            )
            
            return APIResponse(
                success=True,
                message="Registration successful. Please check your email for verification."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/register/senior",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Register new senior",
            description="Register a new senior account requiring admin approval")
async def register_senior(
    registration_data: SeniorRegistrationRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Register new senior with admin approval workflow."""
    try:
        result = await auth_service.register_senior(registration_data.dict())
        
        if result.success:
            # Notify admins of new registration
            background_tasks.add_task(
                auth_service.notify_admin_new_registration,
                result.user_id
            )
            
            return APIResponse(
                success=True,
                message="Registration successful. Admin approval required."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/register/admin",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Register new admin",
            description="Register a new admin account (super admin only)")
async def register_admin(
    registration_data: AdminRegistrationRequest,
    current_admin: BaseUser = Depends(AuthDependencies.get_super_admin),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Register new admin account (super admin access required)."""
    try:
        result = await auth_service.register_admin(
            registration_data.dict(),
            created_by=current_admin.user_id
        )
        
        if result.success:
            return APIResponse(
                success=True,
                message="Admin account created successfully."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin registration failed"
        )


@router.post("/login",
            response_model=LoginResponse,
            summary="User login",
            description="Authenticate user and return JWT tokens")
async def login(
    login_data: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Authenticate user and return access tokens."""
    try:
        result = await auth_service.login(login_data.email, login_data.password)
        
        if result.success:
            return LoginResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type="bearer",
                expires_in=result.expires_in,
                user_id=result.user.user_id,
                user_type=result.user.get_user_type()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error_message,
                headers={"WWW-Authenticate": "Bearer"}
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout",
            response_model=APIResponse,
            summary="User logout",
            description="Invalidate user session and tokens")
async def logout(
    current_user: BaseUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Logout user and invalidate tokens."""
    try:
        await auth_service.logout(current_user.user_id, credentials.credentials)
        
        return APIResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/refresh",
            response_model=LoginResponse,
            summary="Refresh access token",
            description="Get new access token using refresh token")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Refresh access token."""
    try:
        result = await auth_service.refresh_token(refresh_data.refresh_token)
        
        if result.success:
            return LoginResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type="bearer",
                expires_in=result.expires_in,
                user_id=result.user.user_id,
                user_type=result.user.get_user_type()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/verify-email",
           response_model=APIResponse,
           summary="Verify email address",
           description="Verify user email with verification token")
async def verify_email(
    token: str,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Verify user email address."""
    try:
        success = await auth_service.verify_email(token)
        
        if success:
            return APIResponse(
                success=True,
                message="Email verified successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/reset-password-request",
            response_model=APIResponse,
            summary="Request password reset",
            description="Send password reset email to user")
async def reset_password_request(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Request password reset email."""
    try:
        # Send reset email in background
        background_tasks.add_task(
            auth_service.send_password_reset_email,
            reset_data.email
        )
        
        # Always return success for security
        return APIResponse(
            success=True,
            message="If email exists, reset instructions have been sent"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/reset-password",
            response_model=APIResponse,
            summary="Reset password",
            description="Reset password using reset token")
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Reset password with token."""
    try:
        success = await auth_service.reset_password(
            reset_data.reset_token,
            reset_data.new_password
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Password reset successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/change-password",
            response_model=APIResponse,
            summary="Change password",
            description="Change password for authenticated user")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: BaseUser = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Change password for authenticated user."""
    try:
        success = await auth_service.change_password(
            current_user.user_id,
            password_data.current_password,
            password_data.new_password
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Password changed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/identity-verification",
            response_model=APIResponse,
            summary="Submit identity documents",
            description="Upload identity documents for verification")
async def submit_identity_verification(
    documents: List[UploadFile] = File(...),
    document_types: str = Form(...),
    current_user: BaseUser = Depends(get_current_user),
    verification_service: IdentityVerificationService = Depends(get_verification_service)
):
    """Submit identity documents for verification."""
    try:
        # Process uploaded documents
        processed_documents = await _process_uploaded_documents(documents, document_types)
        
        verification_id = await verification_service.submit_identity_documents(
            current_user.user_id,
            processed_documents
        )
        
        return APIResponse(
            success=True,
            message=f"Documents submitted for verification. Verification ID: {verification_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document submission failed"
        )


@router.get("/verification-status",
           response_model=Dict[str, Any],
           summary="Get verification status",
           description="Get identity verification status for current user")
async def get_verification_status(
    current_user: BaseUser = Depends(get_current_user),
    verification_service: IdentityVerificationService = Depends(get_verification_service)
):
    """Get identity verification status."""
    try:
        status_info = await verification_service.check_verification_status(current_user.user_id)
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get verification status"
        )


@router.get("/profile",
           response_model=Dict[str, Any],
           summary="Get user profile",
           description="Get current user profile information")
async def get_current_user_profile(
    current_user: BaseUser = Depends(get_current_user)
):
    """Get current user profile."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "user_type": current_user.get_user_type().value,
        "status": current_user.status.value,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


async def _process_uploaded_documents(documents: List[UploadFile], document_types: str) -> Dict[str, Any]:
    """Process uploaded document files."""
    # Implementation would handle file processing, validation, and storage
    processed = {}
    doc_types = document_types.split(',')
    
    for i, doc in enumerate(documents):
        doc_type = doc_types[i] if i < len(doc_types) else "unknown"
        
        # In a real implementation, you would:
        # 1. Validate file type and size
        # 2. Store file securely
        # 3. Extract metadata
        # 4. Generate secure URL
        
        processed[doc_type] = {
            "filename": doc.filename,
            "content_type": doc.content_type,
            "size": doc.size if hasattr(doc, 'size') else 0,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    return processed


# Export the router
auth_router = router