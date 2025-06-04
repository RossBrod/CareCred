from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict


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


class GPSLocation:
    """GPS location model"""
    
    def __init__(self):
        self.latitude: float = None
        self.longitude: float = None
        self.accuracy: float = None
        self.timestamp: datetime = None
        self.address: str = None
    
    def distance_to(self, other_location: 'GPSLocation') -> float:
        pass
    
    def is_within_radius(self, target_location: 'GPSLocation', radius_meters: float) -> bool:
        pass


class Session:
    """Session model representing a help session between student and senior"""
    
    def __init__(self):
        self.session_id: str = None
        self.student_id: str = None
        self.senior_id: str = None
        self.session_type: SessionType = None
        self.status: SessionStatus = SessionStatus.REQUESTED
        self.title: str = None
        self.description: str = None
        self.scheduled_start_time: datetime = None
        self.scheduled_end_time: datetime = None
        self.actual_start_time: datetime = None
        self.actual_end_time: datetime = None
        self.estimated_duration_hours: float = None
        self.actual_duration_hours: float = None
        self.location: GPSLocation = None
        self.senior_address: str = None
        self.special_instructions: str = None
        self.created_at: datetime = None
        self.updated_at: datetime = None
        
        # Check-in/Check-out tracking
        self.check_in_location: GPSLocation = None
        self.check_out_location: GPSLocation = None
        self.check_in_time: datetime = None
        self.check_out_time: datetime = None
        
        # Ratings and reviews
        self.student_rating: Optional[int] = None  # 1-5 stars
        self.senior_rating: Optional[int] = None   # 1-5 stars
        self.student_review: str = None
        self.senior_review: str = None
        
        # Blockchain and verification
        self.blockchain_transaction_hash: str = None
        self.blockchain_block_number: int = None
        self.verification_status: str = "pending"
        
        # Credit calculation
        self.credit_amount: float = None
        self.hourly_rate: float = 15.00  # Default rate
        self.credit_disbursed: bool = False
    
    def calculate_duration(self) -> float:
        pass
    
    def calculate_credits(self) -> float:
        pass
    
    def start_session(self, gps_location: GPSLocation) -> bool:
        pass
    
    def end_session(self, gps_location: GPSLocation) -> bool:
        pass
    
    def add_student_rating(self, rating: int, review: str = None) -> None:
        pass
    
    def add_senior_rating(self, rating: int, review: str = None) -> None:
        pass
    
    def verify_location(self, current_location: GPSLocation) -> bool:
        pass
    
    def record_on_blockchain(self) -> str:
        pass
    
    def get_session_summary(self) -> Dict:
        pass


class SessionRequest:
    """Model for session requests before they become full sessions"""
    
    def __init__(self):
        self.request_id: str = None
        self.student_id: str = None
        self.senior_id: str = None
        self.session_type: SessionType = None
        self.preferred_date: datetime = None
        self.preferred_time_start: str = None
        self.preferred_time_end: str = None
        self.message: str = None
        self.status: str = "pending"  # pending, approved, rejected
        self.created_at: datetime = None
        self.response_message: str = None
        self.responded_at: datetime = None
    
    def approve(self, response_message: str = None) -> Session:
        pass
    
    def reject(self, reason: str) -> None:
        pass
    
    def convert_to_session(self) -> Session:
        pass


class SessionAlert:
    """Model for session alerts and notifications"""
    
    def __init__(self):
        self.alert_id: str = None
        self.session_id: str = None
        self.alert_type: str = None  # overtime, gps_drift, no_checkin, emergency
        self.severity: str = None    # low, medium, high, critical
        self.message: str = None
        self.created_at: datetime = None
        self.resolved: bool = False
        self.resolved_at: datetime = None
        self.resolved_by: str = None  # admin_id
    
    def resolve(self, admin_id: str, resolution_notes: str = None) -> None:
        pass
    
    def escalate(self, new_severity: str) -> None:
        pass