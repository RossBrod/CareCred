from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Union
from datetime import datetime
from enum import Enum

from ..Models.user import UserType, UserStatus, AdminRole
from ..Models.session import SessionType, SessionStatus, AlertSeverity
from ..Models.credit import CreditTransactionType, DisbursementType, PaymentMethod
from ..Models.messaging import MessageType, NotificationPriority, ConversationType

# Common response schemas
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[dict]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: Dict[str, Union[str, int]]

# Authentication schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    user_type: UserType

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

# User registration schemas
class StudentRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone: Optional[str] = None
    university: str = Field(min_length=1, max_length=100)
    student_id: str = Field(min_length=1, max_length=50)
    major: str = Field(min_length=1, max_length=100)
    graduation_year: int = Field(ge=2020, le=2035)
    bio: Optional[str] = Field(None, max_length=500)
    skills: List[str] = []
    has_transportation: bool = False
    max_travel_distance: float = Field(default=0.0, ge=0.0, le=100.0)

class SeniorRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone: Optional[str] = None
    age: int = Field(ge=55, le=120)
    address: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    zip_code: str = Field(regex=r'^\d{5}(-\d{4})?$')
    emergency_contact_name: str = Field(min_length=1, max_length=100)
    emergency_contact_phone: str = Field(regex=r'^\+?1?\d{9,15}$')
    help_needed: List[str] = []
    mobility_notes: Optional[str] = Field(None, max_length=500)
    medical_notes: Optional[str] = Field(None, max_length=500)

class AdminRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    admin_role: AdminRole
    employee_id: str = Field(min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    permissions: List[str] = []

# User profile schemas
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None

class StudentProfileUpdate(UserProfileUpdate):
    bio: Optional[str] = Field(None, max_length=500)
    skills: Optional[List[str]] = None
    availability_schedule: Optional[Dict[str, List[str]]] = None
    has_transportation: Optional[bool] = None
    max_travel_distance: Optional[float] = Field(None, ge=0.0, le=100.0)

class SeniorProfileUpdate(UserProfileUpdate):
    help_needed: Optional[List[str]] = None
    mobility_notes: Optional[str] = Field(None, max_length=500)
    medical_notes: Optional[str] = Field(None, max_length=500)
    preferred_times: Optional[Dict[str, List[str]]] = None

# Session schemas
class SessionRequestCreate(BaseModel):
    senior_id: str
    session_type: SessionType
    preferred_date: datetime
    preferred_time_start: str = Field(regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    preferred_time_end: str = Field(regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    message: Optional[str] = Field(None, max_length=500)

class SessionRequestResponse(BaseModel):
    approved: bool
    response_message: Optional[str] = Field(None, max_length=500)

class SessionSchedule(BaseModel):
    scheduled_start_time: datetime
    scheduled_end_time: datetime
    estimated_duration_hours: float = Field(gt=0, le=24)
    special_instructions: Optional[str] = Field(None, max_length=500)

class GPSLocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float = Field(ge=0.0)
    address: Optional[str] = Field(None, max_length=300)

class SessionCheckIn(BaseModel):
    location: GPSLocationRequest

class SessionCheckOut(BaseModel):
    location: GPSLocationRequest
    session_notes: Optional[str] = Field(None, max_length=500)

class SessionRating(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: Optional[str] = Field(None, max_length=500)
    rating_categories: Optional[Dict[str, int]] = None

class SessionCancel(BaseModel):
    reason: str = Field(min_length=1, max_length=500)

class SessionReschedule(BaseModel):
    new_datetime: datetime
    reason: Optional[str] = Field(None, max_length=500)

# Credit schemas
class CreditAccountCreate(BaseModel):
    institution_name: str = Field(min_length=1, max_length=200)
    institution_account_number: Optional[str] = Field(None, max_length=50)
    institution_routing_number: Optional[str] = Field(None, max_length=20)

class DisbursementRequest(BaseModel):
    amount: float = Field(gt=0.0)
    disbursement_type: DisbursementType
    allocation_preferences: Optional[Dict[str, float]] = None

class DisbursementApproval(BaseModel):
    approved: bool
    notes: Optional[str] = Field(None, max_length=500)

class CreditAdjustment(BaseModel):
    amount: float
    reason: str = Field(min_length=1, max_length=500)
    adjustment_type: str = "manual"

class DisbursementPreferencesUpdate(BaseModel):
    preferences: Dict[str, float]

# Messaging schemas
class ConversationCreate(BaseModel):
    participants: List[str] = Field(min_items=2, max_items=10)
    subject: Optional[str] = Field(None, max_length=200)
    session_id: Optional[str] = None

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    attachment_url: Optional[str] = Field(None, max_length=500)

class MessageFlag(BaseModel):
    reason: str = Field(min_length=1, max_length=200)

class NotificationPreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    session_reminders: Optional[bool] = None
    session_updates: Optional[bool] = None
    new_messages: Optional[bool] = None
    credit_updates: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    quiet_hours_end: Optional[str] = Field(None, regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')

class EmergencyAlertCreate(BaseModel):
    alert_type: str = Field(regex=r'^(medical|safety|technical|other)$')
    message: str = Field(min_length=1, max_length=1000)
    location: Optional[str] = Field(None, max_length=300)
    session_id: Optional[str] = None

# Admin schemas
class UserApproval(BaseModel):
    approved: bool
    notes: Optional[str] = Field(None, max_length=500)

class AlertResolution(BaseModel):
    resolution_notes: str = Field(min_length=1, max_length=500)

class AlertEscalation(BaseModel):
    new_severity: AlertSeverity

class BulkStatusUpdate(BaseModel):
    item_ids: List[str]
    new_status: str
    reason: Optional[str] = Field(None, max_length=500)

class InstitutionCreate(BaseModel):
    institution_name: str = Field(min_length=1, max_length=200)
    contact_name: str = Field(min_length=1, max_length=100)
    contact_email: EmailStr
    contact_phone: str = Field(regex=r'^\+?1?\d{9,15}$')
    integration_type: str = Field(regex=r'^(direct_api|file_transfer|manual)$')
    api_endpoint: Optional[str] = Field(None, max_length=500)
    account_number: Optional[str] = Field(None, max_length=50)
    routing_number: Optional[str] = Field(None, max_length=20)

class ReportGenerate(BaseModel):
    report_type: str = Field(regex=r'^(monthly|quarterly|annual|custom)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    institution_id: Optional[str] = None

# Response schemas for GET endpoints
class UserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    user_type: UserType
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime]
    rating: float
    total_reviews: int

class SessionResponse(BaseModel):
    session_id: str
    student_id: str
    senior_id: str
    session_type: SessionType
    status: SessionStatus
    title: str
    description: str
    scheduled_start_time: Optional[datetime]
    scheduled_end_time: Optional[datetime]
    actual_duration_hours: Optional[float]
    credit_amount: Optional[float]
    created_at: datetime

class CreditAccountResponse(BaseModel):
    account_id: str
    student_id: str
    total_credits_earned: float
    total_credits_disbursed: float
    available_balance: float
    institution_name: Optional[str]
    created_at: datetime

class TransactionResponse(BaseModel):
    transaction_id: str
    transaction_type: CreditTransactionType
    amount: float
    description: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime]

class ConversationResponse(BaseModel):
    conversation_id: str
    conversation_type: ConversationType
    participants: List[str]
    subject: Optional[str]
    last_message_at: Optional[datetime]
    created_at: datetime

class NotificationResponse(BaseModel):
    notification_id: str
    title: str
    message: str
    notification_type: str
    priority: NotificationPriority
    is_read: bool
    created_at: datetime