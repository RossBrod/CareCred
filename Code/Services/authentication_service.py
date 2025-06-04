from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union, Tuple
from pydantic import BaseModel, Field
from ..Models.user import BaseUser, Student, Senior, Admin, UserStatus, AdminRole


class AuthenticationResult(BaseModel):
    """Result object for authentication operations"""
    
    success: bool = False
    user: Optional[BaseUser] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    requires_verification: bool = False
    
    class Config:
        arbitrary_types_allowed = True


class RegistrationResult(BaseModel):
    """Result object for registration operations"""
    
    success: bool = False
    user_id: Optional[str] = None
    verification_token: Optional[str] = None
    error_message: Optional[str] = None
    requires_admin_approval: bool = True


class LoginAttempt(BaseModel):
    """Model for tracking login attempts"""
    
    email: str
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None


class SecurityEvent(BaseModel):
    """Model for security events and audit logging"""
    
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    event_data: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = "info"  # info, warning, error, critical


class AuthenticationService:
    """Service for handling user authentication and authorization"""
    
    def __init__(self, jwt_secret: str, database_connection, email_service, encryption_service):
        self.jwt_secret: str = jwt_secret
        self.token_expiry_hours: int = 24
        self.refresh_token_expiry_days: int = 30
        self.max_login_attempts: int = 5
        self.lockout_duration_minutes: int = 30
        self.password_min_length: int = 8
        self.require_password_complexity: bool = True
    
    def register_student(self, registration_data: Dict[str, Union[str, int, bool]]) -> RegistrationResult:
        """
        Register a new student user
        
        Args:
            registration_data: Dictionary containing student registration information
                Required fields: email, password, first_name, last_name, university, 
                student_id, major, graduation_year
                Optional fields: phone, bio, skills, has_transportation, max_travel_distance
        
        Returns:
            RegistrationResult with success status and user details or error message
        """
        pass
    
    def register_senior(self, registration_data: Dict[str, Union[str, int, List[str]]]) -> RegistrationResult:
        """
        Register a new senior user
        
        Args:
            registration_data: Dictionary containing senior registration information
                Required fields: email, password, first_name, last_name, age, address,
                city, state, zip_code, emergency_contact_name, emergency_contact_phone
                Optional fields: phone, help_needed, mobility_notes, medical_notes
        
        Returns:
            RegistrationResult with success status and user details or error message
        """
        pass
    
    def register_admin(self, registration_data: Dict[str, Union[str, List[str]]], created_by_admin_id: str) -> RegistrationResult:
        """
        Register a new admin user (admin-only operation)
        
        Args:
            registration_data: Dictionary containing admin registration information
                Required fields: email, password, first_name, last_name, admin_role,
                employee_id
                Optional fields: phone, department, permissions
            created_by_admin_id: ID of admin creating this account
        
        Returns:
            RegistrationResult with success status and user details or error message
        """
        pass
    
    def login(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> AuthenticationResult:
        """
        Authenticate user login
        
        Args:
            email: User's email address
            password: User's password (plain text, will be hashed for comparison)
            ip_address: Client IP address for security logging
            user_agent: Client user agent for security logging
        
        Returns:
            AuthenticationResult with tokens and user data or error message
        """
        pass
    
    def logout(self, user_id: str, token: str) -> bool:
        """
        Logout user and invalidate token
        
        Args:
            user_id: ID of user logging out
            token: JWT token to invalidate
        
        Returns:
            True if logout successful, False otherwise
        """
        pass
    
    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            AuthenticationResult with new access token or error message
        """
        pass
    
    def verify_email(self, verification_token: str) -> bool:
        """
        Verify user email address using verification token
        
        Args:
            verification_token: Email verification token sent to user
        
        Returns:
            True if verification successful, False otherwise
        """
        pass
    
    def reset_password_request(self, email: str) -> bool:
        """
        Send password reset email to user
        
        Args:
            email: User's email address
        
        Returns:
            True if reset email sent successfully, False otherwise
        """
        pass
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Reset password using reset token
        
        Args:
            reset_token: Password reset token from email
            new_password: New password (plain text, will be hashed)
        
        Returns:
            True if password reset successful, False otherwise
        """
        pass
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password (requires current password verification)
        
        Args:
            user_id: ID of user changing password
            current_password: Current password for verification
            new_password: New password (plain text, will be hashed)
        
        Returns:
            True if password change successful, False otherwise
        """
        pass
    
    def validate_token(self, token: str) -> Optional[BaseUser]:
        """
        Validate JWT token and return user object
        
        Args:
            token: JWT access token to validate
        
        Returns:
            User object if token valid, None otherwise
        """
        pass
    
    def check_login_attempts(self, email: str) -> Dict[str, Union[int, bool, datetime]]:
        """
        Check failed login attempts for account lockout
        
        Args:
            email: User's email address
        
        Returns:
            Dictionary with attempt count, locked status, and lockout expiry
        """
        pass
    
    def lock_account(self, user_id: str, reason: str, locked_by_admin_id: str = None) -> None:
        """
        Lock user account
        
        Args:
            user_id: ID of user to lock
            reason: Reason for account lock
            locked_by_admin_id: ID of admin locking account (if applicable)
        """
        pass
    
    def unlock_account(self, user_id: str, admin_id: str) -> None:
        """
        Unlock user account (admin operation)
        
        Args:
            user_id: ID of user to unlock
            admin_id: ID of admin performing unlock
        """
        pass
    
    def get_login_history(self, user_id: str, limit: int = 50) -> List[LoginAttempt]:
        """
        Get user's login history
        
        Args:
            user_id: ID of user
            limit: Maximum number of records to return
        
        Returns:
            List of LoginAttempt objects
        """
        pass
    
    def get_security_events(self, user_id: str = None, event_type: str = None, limit: int = 100) -> List[SecurityEvent]:
        """
        Get security events for auditing
        
        Args:
            user_id: Filter by specific user (optional)
            event_type: Filter by event type (optional)
            limit: Maximum number of records to return
        
        Returns:
            List of SecurityEvent objects
        """
        pass
    
    def generate_jwt_token(self, user: BaseUser) -> str:
        """
        Generate JWT access token for user
        
        Args:
            user: User object to generate token for
        
        Returns:
            JWT token string
        """
        pass
    
    def generate_refresh_token(self, user_id: str) -> str:
        """
        Generate refresh token for user
        
        Args:
            user_id: ID of user
        
        Returns:
            Refresh token string
        """
        pass
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using secure algorithm (bcrypt)
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        pass
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
        
        Returns:
            True if password matches, False otherwise
        """
        pass
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password meets security requirements
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        pass


class IdentityVerificationService:
    """Service for handling identity verification and background checks"""
    
    def __init__(self, background_check_provider: str = "checkr", id_verification_provider: str = "jumio"):
        self.background_check_provider = background_check_provider
        self.id_verification_provider = id_verification_provider
        self.max_verification_attempts = 3
        self.document_retention_days = 2555  # 7 years for compliance
    
    def submit_identity_documents(self, user_id: str, documents: Dict[str, str]) -> str:
        """
        Submit identity documents for verification
        
        Args:
            user_id: ID of user submitting documents
            documents: Dictionary mapping document type to file path/URL
                Expected types: 'drivers_license', 'passport', 'student_id'
        
        Returns:
            Verification request ID for tracking
        """
        pass
    
    def initiate_background_check(self, user_id: str, check_type: str = "standard") -> str:
        """
        Initiate background check process
        
        Args:
            user_id: ID of user to check
            check_type: Type of check ('standard', 'enhanced', 'basic')
        
        Returns:
            Background check request ID
        """
        pass
    
    def check_verification_status(self, user_id: str) -> Dict[str, Union[str, bool, datetime]]:
        """
        Check status of identity verification
        
        Args:
            user_id: ID of user to check
        
        Returns:
            Dictionary with verification status, completion date, and details
        """
        pass
    
    def approve_verification(self, user_id: str, admin_id: str, notes: str = None) -> bool:
        """
        Manually approve identity verification
        
        Args:
            user_id: ID of user to approve
            admin_id: ID of admin approving
            notes: Optional approval notes
        
        Returns:
            True if approval successful
        """
        pass
    
    def reject_verification(self, user_id: str, admin_id: str, reason: str) -> bool:
        """
        Reject identity verification with reason
        
        Args:
            user_id: ID of user to reject
            admin_id: ID of admin rejecting
            reason: Reason for rejection
        
        Returns:
            True if rejection recorded successfully
        """
        pass
    
    def get_background_check_results(self, user_id: str) -> Dict[str, Union[str, bool, List[Dict]]]:
        """
        Get background check results
        
        Args:
            user_id: ID of user
        
        Returns:
            Dictionary with check status, results, and any flags
        """
        pass
    
    def store_verification_documents(self, user_id: str, documents: List[Dict[str, str]]) -> List[str]:
        """
        Securely store verification documents
        
        Args:
            user_id: ID of user
            documents: List of document metadata and encrypted content
        
        Returns:
            List of document IDs for reference
        """
        pass
    
    def delete_verification_documents(self, user_id: str) -> bool:
        """
        Delete verification documents (privacy compliance)
        
        Args:
            user_id: ID of user whose documents to delete
        
        Returns:
            True if deletion successful
        """
        pass


class AuthorizationService:
    """Service for handling user permissions and authorization"""
    
    def __init__(self):
        self.role_permissions: Dict[str, List[str]] = {
            "student": [
                "view_own_profile", "edit_own_profile", "create_session_request",
                "view_own_sessions", "rate_sessions", "message_participants"
            ],
            "senior": [
                "view_own_profile", "edit_own_profile", "respond_to_requests",
                "view_own_sessions", "rate_sessions", "message_participants"
            ],
            "admin": [
                "view_all_users", "approve_users", "manage_sessions", "view_reports",
                "manage_credits", "moderate_content", "send_notifications"
            ],
            "super_admin": ["all_permissions"]
        }
    
    def has_permission(self, user: BaseUser, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user: User object to check
            permission: Permission string to verify
        
        Returns:
            True if user has permission, False otherwise
        """
        pass
    
    def get_user_permissions(self, user: BaseUser) -> List[str]:
        """
        Get all permissions for user based on role
        
        Args:
            user: User object
        
        Returns:
            List of permission strings
        """
        pass
    
    def can_access_resource(self, user: BaseUser, resource_type: str, resource_id: str) -> bool:
        """
        Check if user can access specific resource
        
        Args:
            user: User object
            resource_type: Type of resource ('session', 'user', 'credit_account', etc.)
            resource_id: ID of specific resource
        
        Returns:
            True if access allowed, False otherwise
        """
        pass
    
    def can_modify_resource(self, user: BaseUser, resource_type: str, resource_id: str) -> bool:
        """
        Check if user can modify specific resource
        
        Args:
            user: User object
            resource_type: Type of resource
            resource_id: ID of specific resource
        
        Returns:
            True if modification allowed, False otherwise
        """
        pass
    
    def require_admin_permission(self, user: BaseUser, permission: str) -> bool:
        """
        Require admin-level permission
        
        Args:
            user: User object to check
            permission: Admin permission required
        
        Returns:
            True if user has admin permission, False otherwise
        """
        pass
    
    def audit_permission_check(self, user_id: str, permission: str, resource: str, granted: bool) -> None:
        """
        Log permission check for audit trail
        
        Args:
            user_id: ID of user
            permission: Permission checked
            resource: Resource accessed
            granted: Whether permission was granted
        """
        pass
    
    def get_role_hierarchy(self) -> Dict[str, int]:
        """
        Get role hierarchy for permission inheritance
        
        Returns:
            Dictionary mapping roles to hierarchy levels
        """
        pass
    
    def check_resource_ownership(self, user_id: str, resource_type: str, resource_id: str) -> bool:
        """
        Check if user owns the specified resource
        
        Args:
            user_id: ID of user
            resource_type: Type of resource
            resource_id: ID of resource
        
        Returns:
            True if user owns resource, False otherwise
        """
        pass