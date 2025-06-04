from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from uuid import uuid4


class SessionStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SessionType(Enum):
    GROCERY_SHOPPING = "grocery_shopping"
    TECHNOLOGY_HELP = "technology_help"
    TRANSPORTATION = "transportation"
    COMPANIONSHIP = "companionship"
    LIGHT_HOUSEKEEPING = "light_housekeeping"
    MEAL_PREPARATION = "meal_preparation"
    PET_CARE = "pet_care"
    HOME_MAINTENANCE = "home_maintenance"
    MEDICAL_APPOINTMENT = "medical_appointment"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GPSLocation(BaseModel):
    """GPS location model"""
    
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float = Field(ge=0.0, description="GPS accuracy in meters")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    address: Optional[str] = Field(None, max_length=300)
    
    class Config:
        validate_assignment = True
    
    @validator('accuracy')
    def validate_accuracy(cls, v):
        if v > 1000:  # 1km accuracy limit
            raise ValueError('GPS accuracy too low')
        return v
    
    def distance_to(self, other_location: 'GPSLocation') -> float:
        """Calculate distance in meters to another GPS location"""
        pass
    
    def is_within_radius(self, target_location: 'GPSLocation', radius_meters: float) -> bool:
        """Check if location is within specified radius of target"""
        pass


class Session(BaseModel):
    """Session model representing a help session between student and senior"""
    
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    student_id: str = Field(min_length=1)
    senior_id: str = Field(min_length=1)
    session_type: SessionType
    status: SessionStatus = SessionStatus.REQUESTED
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=1000)
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    estimated_duration_hours: float = Field(gt=0, le=24)
    actual_duration_hours: Optional[float] = Field(None, ge=0, le=24)
    location: Optional[GPSLocation] = None
    senior_address: str = Field(min_length=1, max_length=300)
    special_instructions: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Check-in/Check-out tracking
    check_in_location: Optional[GPSLocation] = None
    check_out_location: Optional[GPSLocation] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    
    # Ratings and reviews
    student_rating: Optional[int] = Field(None, ge=1, le=5)
    senior_rating: Optional[int] = Field(None, ge=1, le=5)
    student_review: Optional[str] = Field(None, max_length=500)
    senior_review: Optional[str] = Field(None, max_length=500)
    
    # Blockchain and verification
    blockchain_transaction_hash: Optional[str] = None
    blockchain_block_number: Optional[int] = None
    blockchain_confirmations: int = Field(default=0)
    verification_status: str = Field(default="pending")
    signature_request_id: Optional[str] = None
    student_signature: Optional[str] = None
    senior_signature: Optional[str] = None
    session_hash: Optional[str] = None
    blockchain_verified: bool = False
    blockchain_verified_at: Optional[datetime] = None
    
    # Credit calculation
    credit_amount: Optional[float] = Field(None, ge=0.0)
    hourly_rate: float = Field(default=15.00, gt=0.0, le=100.0)
    credit_disbursed: bool = False
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('scheduled_end_time')
    def validate_end_time(cls, v, values):
        if v and 'scheduled_start_time' in values and values['scheduled_start_time']:
            if v <= values['scheduled_start_time']:
                raise ValueError('End time must be after start time')
        return v
    
    @validator('actual_end_time')
    def validate_actual_end_time(cls, v, values):
        if v and 'actual_start_time' in values and values['actual_start_time']:
            if v <= values['actual_start_time']:
                raise ValueError('Actual end time must be after actual start time')
        return v
    
    def calculate_duration(self) -> float:
        """Calculate actual session duration in hours"""
        pass
    
    def calculate_credits(self) -> float:
        """Calculate credits earned for this session"""
        pass
    
    def start_session(self, gps_location: GPSLocation) -> bool:
        """Start session with GPS verification"""
        pass
    
    def end_session(self, gps_location: GPSLocation) -> bool:
        """End session with GPS verification"""
        pass
    
    def add_student_rating(self, rating: int, review: str = None) -> None:
        """Add student rating and review"""
        pass
    
    def add_senior_rating(self, rating: int, review: str = None) -> None:
        """Add senior rating and review"""
        pass
    
    def verify_location(self, current_location: GPSLocation) -> bool:
        """Verify current location matches session location"""
        pass
    
    def record_on_blockchain(self) -> str:
        """Record session completion on blockchain"""
        pass
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        pass


class SessionRequest(BaseModel):
    """Model for session requests before they become full sessions"""
    
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    student_id: str = Field(min_length=1)
    senior_id: str = Field(min_length=1)
    session_type: SessionType
    preferred_date: datetime
    preferred_time_start: str = Field(regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    preferred_time_end: str = Field(regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    message: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="pending", regex=r'^(pending|approved|rejected)$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response_message: Optional[str] = Field(None, max_length=500)
    responded_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('preferred_time_end')
    def validate_time_range(cls, v, values):
        if 'preferred_time_start' in values:
            start_time = values['preferred_time_start']
            if v <= start_time:
                raise ValueError('End time must be after start time')
        return v
    
    def approve(self, response_message: str = None) -> 'Session':
        """Approve request and convert to session"""
        pass
    
    def reject(self, reason: str) -> None:
        """Reject session request"""
        pass
    
    def convert_to_session(self) -> 'Session':
        """Convert approved request to scheduled session"""
        pass


class SessionAlert(BaseModel):
    """Model for session alerts and notifications"""
    
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(min_length=1)
    alert_type: str = Field(regex=r'^(overtime|gps_drift|no_checkin|emergency|inactivity)$')
    severity: AlertSeverity
    message: str = Field(min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None  # admin_id
    resolution_notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def resolve(self, admin_id: str, resolution_notes: str = None) -> None:
        """Resolve alert with admin action"""
        pass
    
    def escalate(self, new_severity: AlertSeverity) -> None:
        """Escalate alert to higher severity level"""
        pass