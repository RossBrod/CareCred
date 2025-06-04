from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, List


class UserType(Enum):
    STUDENT = "student"
    SENIOR = "senior"
    ADMIN = "admin"


class UserStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class BaseUser(ABC):
    """Abstract base class for all user types"""
    
    def __init__(self):
        self.user_id: str = None
        self.email: str = None
        self.password_hash: str = None
        self.first_name: str = None
        self.last_name: str = None
        self.phone: str = None
        self.profile_photo_url: str = None
        self.status: UserStatus = UserStatus.PENDING
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.last_login: datetime = None
        self.email_verified: bool = False
        self.background_check_status: str = None
        self.rating: float = 0.0
        self.total_reviews: int = 0
    
    @abstractmethod
    def get_user_type(self) -> UserType:
        pass
    
    def update_rating(self, new_rating: float) -> None:
        pass
    
    def verify_email(self) -> bool:
        pass
    
    def set_background_check_status(self, status: str) -> None:
        pass


class Student(BaseUser):
    """Student user model"""
    
    def __init__(self):
        super().__init__()
        self.university: str = None
        self.student_id: str = None
        self.major: str = None
        self.graduation_year: int = None
        self.bio: str = None
        self.skills: List[str] = []
        self.availability_schedule: dict = {}
        self.has_transportation: bool = False
        self.max_travel_distance: float = 0.0
        self.total_credits_earned: float = 0.0
        self.total_hours_completed: float = 0.0
        self.active_sessions_count: int = 0
    
    def get_user_type(self) -> UserType:
        return UserType.STUDENT
    
    def add_skill(self, skill: str) -> None:
        pass
    
    def remove_skill(self, skill: str) -> None:
        pass
    
    def update_availability(self, schedule: dict) -> None:
        pass
    
    def add_credits(self, amount: float) -> None:
        pass
    
    def get_credit_balance(self) -> float:
        pass


class Senior(BaseUser):
    """Senior user model"""
    
    def __init__(self):
        super().__init__()
        self.age: int = None
        self.address: str = None
        self.city: str = None
        self.state: str = None
        self.zip_code: str = None
        self.emergency_contact_name: str = None
        self.emergency_contact_phone: str = None
        self.help_needed: List[str] = []
        self.mobility_notes: str = None
        self.medical_notes: str = None
        self.preferred_times: dict = {}
        self.total_sessions_completed: int = 0
        self.total_hours_received: float = 0.0
    
    def get_user_type(self) -> UserType:
        return UserType.SENIOR
    
    def add_help_type(self, help_type: str) -> None:
        pass
    
    def remove_help_type(self, help_type: str) -> None:
        pass
    
    def update_emergency_contact(self, name: str, phone: str) -> None:
        pass
    
    def update_address(self, address: str, city: str, state: str, zip_code: str) -> None:
        pass


class Admin(BaseUser):
    """Admin user model"""
    
    def __init__(self):
        super().__init__()
        self.admin_role: str = None  # super_admin, moderator, support
        self.permissions: List[str] = []
        self.department: str = None
        self.employee_id: str = None
        self.last_action_timestamp: datetime = None
    
    def get_user_type(self) -> UserType:
        return UserType.ADMIN
    
    def has_permission(self, permission: str) -> bool:
        pass
    
    def add_permission(self, permission: str) -> None:
        pass
    
    def log_action(self, action: str, details: dict) -> None:
        pass