from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import uuid4


class UserType(Enum):
    STUDENT = "student"
    SENIOR = "senior"
    ADMIN = "admin"


class UserStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class AdminRole(Enum):
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    FINANCIAL = "financial"


class BaseUser(BaseModel, ABC):
    """Abstract base class for all user types"""
    
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    password_hash: str = Field(exclude=True)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    profile_photo_url: Optional[str] = None
    status: UserStatus = UserStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    email_verified: bool = False
    background_check_status: Optional[str] = None
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0, ge=0)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @abstractmethod
    def get_user_type(self) -> UserType:
        pass
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v
    
    def update_rating(self, new_rating: float) -> None:
        """Update user rating based on new review"""
        pass
    
    def verify_email(self) -> bool:
        """Mark email as verified"""
        pass
    
    def set_background_check_status(self, status: str) -> None:
        """Update background check status"""
        pass


class Student(BaseUser):
    """Student user model"""
    
    university: str = Field(min_length=1, max_length=100)
    student_id: str = Field(min_length=1, max_length=50)
    major: str = Field(min_length=1, max_length=100)
    graduation_year: int = Field(ge=2020, le=2035)
    bio: Optional[str] = Field(None, max_length=500)
    skills: List[str] = Field(default_factory=list)
    availability_schedule: Dict[str, List[str]] = Field(default_factory=dict)
    has_transportation: bool = False
    max_travel_distance: float = Field(default=0.0, ge=0.0, le=100.0)
    total_credits_earned: float = Field(default=0.0, ge=0.0)
    total_hours_completed: float = Field(default=0.0, ge=0.0)
    active_sessions_count: int = Field(default=0, ge=0)
    
    def get_user_type(self) -> UserType:
        return UserType.STUDENT
    
    @validator('skills')
    def validate_skills(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 skills allowed')
        return v
    
    @validator('availability_schedule')
    def validate_schedule(cls, v):
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in v.keys():
            if day.lower() not in valid_days:
                raise ValueError(f'Invalid day: {day}')
        return v
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to student's profile"""
        pass
    
    def remove_skill(self, skill: str) -> None:
        """Remove a skill from student's profile"""
        pass
    
    def update_availability(self, schedule: dict) -> None:
        """Update availability schedule"""
        pass
    
    def add_credits(self, amount: float) -> None:
        """Add credits to student's account"""
        pass
    
    def get_credit_balance(self) -> float:
        """Get current credit balance"""
        pass


class Senior(BaseUser):
    """Senior user model"""
    
    age: int = Field(ge=55, le=120)
    address: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    zip_code: str = Field(regex=r'^\d{5}(-\d{4})?$')
    emergency_contact_name: str = Field(min_length=1, max_length=100)
    emergency_contact_phone: str = Field(regex=r'^\+?1?\d{9,15}$')
    help_needed: List[str] = Field(default_factory=list)
    mobility_notes: Optional[str] = Field(None, max_length=500)
    medical_notes: Optional[str] = Field(None, max_length=500)
    preferred_times: Dict[str, List[str]] = Field(default_factory=dict)
    total_sessions_completed: int = Field(default=0, ge=0)
    total_hours_received: float = Field(default=0.0, ge=0.0)
    
    def get_user_type(self) -> UserType:
        return UserType.SENIOR
    
    @validator('help_needed')
    def validate_help_needed(cls, v):
        if len(v) > 15:
            raise ValueError('Maximum 15 help types allowed')
        return v
    
    def add_help_type(self, help_type: str) -> None:
        """Add type of help needed"""
        pass
    
    def remove_help_type(self, help_type: str) -> None:
        """Remove type of help needed"""
        pass
    
    def update_emergency_contact(self, name: str, phone: str) -> None:
        """Update emergency contact information"""
        pass
    
    def update_address(self, address: str, city: str, state: str, zip_code: str) -> None:
        """Update address information"""
        pass


class Admin(BaseUser):
    """Admin user model"""
    
    admin_role: AdminRole
    permissions: List[str] = Field(default_factory=list)
    department: Optional[str] = Field(None, max_length=100)
    employee_id: str = Field(min_length=1, max_length=50)
    last_action_timestamp: Optional[datetime] = None
    
    def get_user_type(self) -> UserType:
        return UserType.ADMIN
    
    @validator('permissions')
    def validate_permissions(cls, v):
        valid_permissions = [
            'view_all_users', 'edit_users', 'approve_users', 'manage_sessions',
            'view_reports', 'manage_credits', 'process_disbursements', 'system_admin'
        ]
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f'Invalid permission: {perm}')
        return v
    
    def has_permission(self, permission: str) -> bool:
        """Check if admin has specific permission"""
        pass
    
    def add_permission(self, permission: str) -> None:
        """Add permission to admin"""
        pass
    
    def log_action(self, action: str, details: dict) -> None:
        """Log admin action for audit trail"""
        pass