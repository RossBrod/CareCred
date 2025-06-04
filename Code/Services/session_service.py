from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Union
from pydantic import BaseModel
from ..Models.session import (
    Session, SessionRequest, SessionStatus, SessionType, GPSLocation, 
    SessionAlert, AlertSeverity
)
from ..Models.user import Student, Senior
from ..Models.blockchain import SessionLog, SignatureRequest, VerificationResult
from .blockchain_service import (
    SolanaService, SignatureService, HashingService, BlockchainVerificationService
)


class SessionMatchingResult(BaseModel):
    """Result object for session matching operations"""
    
    success: bool = False
    matches: List[Dict[str, Union[str, float]]] = []
    compatibility_scores: List[float] = []
    error_message: Optional[str] = None
    total_matches_found: int = 0


class SessionAnalytics(BaseModel):
    """Result object for session analytics"""
    
    total_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    average_duration: float
    average_rating: float
    total_credits_earned: float
    most_popular_service_types: List[Dict[str, Union[str, int]]]
    
    class Config:
        arbitrary_types_allowed = True


class LocationValidationResult(BaseModel):
    """Result object for location validation"""
    
    is_valid: bool
    distance_meters: float
    within_acceptable_radius: bool
    accuracy_acceptable: bool
    validation_timestamp: datetime
    error_message: Optional[str] = None


class SessionService:
    """Service for managing help sessions between students and seniors"""
    
    def __init__(self, database_connection, notification_service, geolocation_service, 
                 blockchain_services: Dict[str, Union[SolanaService, SignatureService, HashingService, BlockchainVerificationService]]):
        self.default_session_duration: float = 2.0  # hours
        self.max_session_duration: float = 8.0
        self.gps_verification_radius: float = 50.0  # meters
        self.overtime_threshold_minutes: int = 30
        self.checkin_reminder_minutes: int = 15
        self.max_sessions_per_day: int = 3
        
        # Blockchain services
        self.solana_service = blockchain_services.get('solana')
        self.signature_service = blockchain_services.get('signature')
        self.hashing_service = blockchain_services.get('hashing')
        self.verification_service = blockchain_services.get('verification')
        self.blockchain_enabled = all([
            self.solana_service, self.signature_service, 
            self.hashing_service, self.verification_service
        ])
    
    def create_session_request(self, student_id: str, senior_id: str, request_data: Dict[str, Union[str, datetime, float]]) -> str:
        """
        Create a new session request from student to senior
        
        Args:
            student_id: ID of student requesting help
            senior_id: ID of senior being requested to help
            request_data: Dictionary containing session request details
                Required fields: session_type, preferred_date, preferred_time_start,
                preferred_time_end, message (optional)
        
        Returns:
            Session request ID for tracking
        """
        pass
    
    def respond_to_session_request(self, request_id: str, senior_id: str, approved: bool, message: str = None) -> bool:
        """
        Senior responds to session request
        
        Args:
            request_id: ID of session request
            senior_id: ID of senior responding
            approved: Whether request is approved or rejected
            message: Optional response message
        
        Returns:
            True if response recorded successfully
        """
        pass
    
    def schedule_session(self, request_id: str, admin_id: str = None) -> Optional[Session]:
        """
        Convert approved request to scheduled session
        
        Args:
            request_id: ID of approved session request
            admin_id: Optional admin ID if manually scheduled
        
        Returns:
            Session object if scheduling successful, None otherwise
        """
        pass
    
    def cancel_session(self, session_id: str, user_id: str, reason: str, cancellation_fee: bool = False) -> bool:
        """
        Cancel a scheduled session
        
        Args:
            session_id: ID of session to cancel
            user_id: ID of user cancelling (student, senior, or admin)
            reason: Reason for cancellation
            cancellation_fee: Whether to apply cancellation fee
        
        Returns:
            True if cancellation successful
        """
        pass
    
    def reschedule_session(self, session_id: str, new_datetime: datetime, requested_by: str, reason: str = None) -> bool:
        """
        Reschedule an existing session
        
        Args:
            session_id: ID of session to reschedule
            new_datetime: New scheduled start time
            requested_by: ID of user requesting reschedule
            reason: Optional reason for reschedule
        
        Returns:
            True if reschedule successful
        """
        pass
    
    def check_in_session(self, session_id: str, user_id: str, gps_location: GPSLocation) -> Tuple[bool, str]:
        """
        Check in to start a session with GPS verification
        
        Args:
            session_id: ID of session to check into
            user_id: ID of user checking in
            gps_location: Current GPS location for verification
        
        Returns:
            Tuple of (success, error_message_if_failed)
        """
        pass
    
    def check_out_session(self, session_id: str, user_id: str, gps_location: GPSLocation, session_notes: str = None) -> Tuple[bool, str]:
        """
        Check out to end a session with GPS verification
        
        Args:
            session_id: ID of session to check out of
            user_id: ID of user checking out
            gps_location: Current GPS location for verification
            session_notes: Optional notes about session completion
        
        Returns:
            Tuple of (success, error_message_if_failed)
        """
        pass
    
    def get_active_sessions(self, user_id: str = None, include_pending: bool = True) -> List[Session]:
        """
        Get currently active sessions, optionally filtered by user
        
        Args:
            user_id: Optional user ID to filter sessions
            include_pending: Whether to include pending check-ins
        
        Returns:
            List of active Session objects
        """
        pass
    
    def get_upcoming_sessions(self, user_id: str, days_ahead: int = 7, session_type: SessionType = None) -> List[Session]:
        """
        Get upcoming sessions for a user
        
        Args:
            user_id: ID of user (student or senior)
            days_ahead: Number of days to look ahead
            session_type: Optional filter by session type
        
        Returns:
            List of upcoming Session objects
        """
        pass
    
    def get_session_history(self, user_id: str, limit: int = 50, offset: int = 0, status_filter: SessionStatus = None) -> List[Session]:
        """
        Get session history for a user
        
        Args:
            user_id: ID of user
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip (for pagination)
            status_filter: Optional filter by session status
        
        Returns:
            List of historical Session objects
        """
        pass
    
    def submit_session_rating(self, session_id: str, rater_id: str, rating: int, review: str = None, rating_categories: Dict[str, int] = None) -> bool:
        """
        Submit rating and review for completed session
        
        Args:
            session_id: ID of completed session
            rater_id: ID of user submitting rating
            rating: Overall rating (1-5 stars)
            review: Optional written review
            rating_categories: Optional category-specific ratings
        
        Returns:
            True if rating submitted successfully
        """
        pass
    
    def verify_session_location(self, session_id: str, current_location: GPSLocation) -> LocationValidationResult:
        """
        Verify if current location matches session location
        
        Args:
            session_id: ID of session to verify
            current_location: Current GPS location
        
        Returns:
            LocationValidationResult with validation details
        """
        pass
    
    def detect_session_anomalies(self, session_id: str) -> List[SessionAlert]:
        """
        Detect anomalies in session (overtime, location drift, etc.)
        
        Args:
            session_id: ID of session to check
        
        Returns:
            List of SessionAlert objects for any anomalies found
        """
        pass
    
    def extend_session(self, session_id: str, additional_hours: float, requested_by: str, reason: str = None) -> Tuple[bool, str]:
        """
        Extend session duration (requires both parties' consent)
        
        Args:
            session_id: ID of session to extend
            additional_hours: Additional time in hours
            requested_by: ID of user requesting extension
            reason: Optional reason for extension
        
        Returns:
            Tuple of (success, message)
        """
        pass
    
    def emergency_end_session(self, session_id: str, admin_id: str, reason: str, notify_authorities: bool = False) -> bool:
        """
        Emergency session termination by admin
        
        Args:
            session_id: ID of session to terminate
            admin_id: ID of admin performing termination
            reason: Reason for emergency termination
            notify_authorities: Whether to notify emergency contacts/authorities
        
        Returns:
            True if termination successful
        """
        pass
    
    def calculate_session_credits(self, session: Session) -> float:
        """
        Calculate credits earned for completed session
        
        Args:
            session: Completed session object
        
        Returns:
            Credit amount earned
        """
        pass
    
    def get_session_analytics(self, start_date: datetime, end_date: datetime, user_id: str = None, session_type: SessionType = None) -> SessionAnalytics:
        """
        Get session analytics for date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            user_id: Optional filter by specific user
            session_type: Optional filter by session type
        
        Returns:
            SessionAnalytics object with comprehensive metrics
        """
        pass
    
    def get_session_details(self, session_id: str, requesting_user_id: str) -> Optional[Session]:
        """
        Get detailed session information
        
        Args:
            session_id: ID of session
            requesting_user_id: ID of user requesting details (for authorization)
        
        Returns:
            Session object if authorized, None otherwise
        """
        pass
    
    async def complete_session_with_blockchain(self, session_id: str, completing_user_id: str, 
                                             gps_location: GPSLocation, session_notes: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Complete session and initiate blockchain logging workflow.
        
        Args:
            session_id: ID of session to complete
            completing_user_id: ID of user completing session
            gps_location: Final GPS location for verification
            session_notes: Optional completion notes
            
        Returns:
            Tuple of (success, message, signature_request_id)
        """
        pass
    
    async def initiate_blockchain_signature_collection(self, session: Session) -> Optional[SignatureRequest]:
        """
        Initiate digital signature collection for completed session.
        
        Args:
            session: Completed session object
            
        Returns:
            SignatureRequest if successful, None otherwise
        """
        pass
    
    async def finalize_session_on_blockchain(self, session_id: str, signature_request: SignatureRequest) -> Tuple[bool, str]:
        """
        Write completed session with signatures to blockchain.
        
        Args:
            session_id: Session to write to blockchain
            signature_request: Completed signature collection
            
        Returns:
            Tuple of (success, transaction_id_or_error)
        """
        pass
    
    async def verify_session_blockchain_integrity(self, session_id: str) -> VerificationResult:
        """
        Verify session data integrity on blockchain.
        
        Args:
            session_id: Session to verify
            
        Returns:
            VerificationResult with complete verification status
        """
        pass
    
    async def get_session_blockchain_proof(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Get public blockchain proof for session verification.
        
        Args:
            session_id: Session to get proof for
            
        Returns:
            Dictionary with proof data and verification URLs
        """
        pass
    
    def prepare_session_for_blockchain(self, session: Session) -> SessionLog:
        """
        Convert completed Session to SessionLog for blockchain storage.
        
        Args:
            session: Completed session object
            
        Returns:
            SessionLog ready for blockchain writing
        """
        pass
    
    async def handle_blockchain_failure(self, session_id: str, error_message: str) -> None:
        """
        Handle blockchain operation failures gracefully.
        
        Args:
            session_id: Session that failed blockchain operation
            error_message: Error details
        """
        pass
    
    async def retry_failed_blockchain_operations(self) -> List[str]:
        """
        Retry sessions with failed blockchain operations.
        
        Returns:
            List of session IDs that were successfully retried
        """
        pass
    
    def bulk_update_session_status(self, session_ids: List[str], new_status: SessionStatus, admin_id: str, reason: str = None) -> Dict[str, bool]:
        """
        Bulk update multiple sessions' status (admin operation)
        
        Args:
            session_ids: List of session IDs to update
            new_status: New status to set
            admin_id: ID of admin performing update
            reason: Optional reason for bulk update
        
        Returns:
            Dictionary mapping session_id to success status
        """
        pass


class SessionMatchingService:
    """Service for matching students with seniors"""
    
    def __init__(self, geolocation_service, user_service):
        self.max_distance_miles: float = 10.0
        self.compatibility_weights: Dict[str, float] = {
            "distance": 0.3,
            "availability": 0.25,
            "skills_match": 0.2,
            "rating": 0.15,
            "experience": 0.1
        }
        self.min_compatibility_score: float = 0.6
    
    def find_available_seniors(self, student_id: str, service_type: SessionType = None, preferred_time: datetime = None, max_distance: float = None) -> SessionMatchingResult:
        """
        Find available seniors for a student to request help from
        
        Args:
            student_id: ID of student looking for help
            service_type: Optional preferred service type
            preferred_time: Optional preferred session time
            max_distance: Optional maximum distance in miles
        
        Returns:
            SessionMatchingResult with available seniors and compatibility scores
        """
        pass
    
    def find_available_students(self, senior_id: str, service_type: SessionType = None, preferred_time: datetime = None) -> SessionMatchingResult:
        """
        Find available students to help a senior
        
        Args:
            senior_id: ID of senior needing help
            service_type: Optional service type needed
            preferred_time: Optional preferred session time
        
        Returns:
            SessionMatchingResult with available students and compatibility scores
        """
        pass
    
    def calculate_compatibility_score(self, student: Student, senior: Senior, service_type: SessionType) -> float:
        """
        Calculate compatibility score between student and senior
        
        Args:
            student: Student object
            senior: Senior object
            service_type: Type of service requested
        
        Returns:
            Compatibility score between 0.0 and 1.0
        """
        pass
    
    def suggest_optimal_matches(self, unmatched_requests: List[SessionRequest], max_suggestions: int = 10) -> List[Dict[str, Union[str, float, List[str]]]]:
        """
        Suggest optimal matches for pending requests using ML/algorithm
        
        Args:
            unmatched_requests: List of pending session requests
            max_suggestions: Maximum number of suggestions per request
        
        Returns:
            List of match suggestions with compatibility scores and reasons
        """
        pass
    
    def manual_match_creation(self, student_id: str, senior_id: str, admin_id: str, session_data: Dict[str, Union[str, datetime]]) -> Optional[Session]:
        """
        Admin creates manual match between student and senior
        
        Args:
            student_id: ID of student
            senior_id: ID of senior
            admin_id: ID of admin creating match
            session_data: Session details (type, time, location, etc.)
        
        Returns:
            Session object if match creation successful
        """
        pass
    
    def check_availability_overlap(self, student_id: str, senior_id: str, proposed_time: datetime, duration_hours: float = 2.0) -> bool:
        """
        Check if student and senior are both available at proposed time
        
        Args:
            student_id: ID of student
            senior_id: ID of senior
            proposed_time: Proposed session start time
            duration_hours: Expected session duration
        
        Returns:
            True if both parties are available
        """
        pass
    
    def calculate_distance(self, student_location: str, senior_location: str) -> float:
        """
        Calculate distance between student and senior locations
        
        Args:
            student_location: Student's address or coordinates
            senior_location: Senior's address or coordinates
        
        Returns:
            Distance in miles
        """
        pass
    
    def filter_by_skills(self, students: List[Student], required_skills: List[str], minimum_matches: int = 1) -> List[Student]:
        """
        Filter students by required skills for service type
        
        Args:
            students: List of student objects
            required_skills: List of skills required
            minimum_matches: Minimum number of skills that must match
        
        Returns:
            List of students with matching skills
        """
        pass
    
    def get_matching_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Union[float, int]]:
        """
        Get statistics about matching success rates
        
        Args:
            start_date: Optional start date for statistics
            end_date: Optional end date for statistics
        
        Returns:
            Dictionary with matching metrics and success rates
        """
        pass
    
    def update_matching_algorithm_weights(self, new_weights: Dict[str, float], admin_id: str) -> bool:
        """
        Update matching algorithm weights (admin operation)
        
        Args:
            new_weights: New weight values for matching factors
            admin_id: ID of admin making changes
        
        Returns:
            True if update successful
        """
        pass


class SessionMonitoringService:
    """Service for monitoring active sessions and detecting issues"""
    
    def __init__(self, notification_service, geolocation_service):
        self.monitoring_interval_minutes: int = 15
        self.gps_drift_threshold_meters: float = 100.0
        self.no_activity_alert_minutes: int = 60
        self.auto_alert_enabled: bool = True
        self.emergency_escalation_minutes: int = 30
    
    def monitor_active_sessions(self) -> List[SessionAlert]:
        """
        Monitor all active sessions for issues
        
        Returns:
            List of SessionAlert objects for any issues detected
        """
        pass
    
    def check_session_overtime(self, session: Session) -> Optional[SessionAlert]:
        """
        Check if session is running overtime
        
        Args:
            session: Session object to check
        
        Returns:
            SessionAlert if overtime detected, None otherwise
        """
        pass
    
    def check_gps_anomalies(self, session: Session, current_location: GPSLocation) -> Optional[SessionAlert]:
        """
        Check for GPS location anomalies
        
        Args:
            session: Session object
            current_location: Current GPS location
        
        Returns:
            SessionAlert if anomaly detected, None otherwise
        """
        pass
    
    def check_no_activity(self, session: Session) -> Optional[SessionAlert]:
        """
        Check for sessions with no recent activity
        
        Args:
            session: Session object to check
        
        Returns:
            SessionAlert if no activity detected, None otherwise
        """
        pass
    
    def create_alert(self, session_id: str, alert_type: str, severity: AlertSeverity, message: str, auto_generated: bool = True) -> SessionAlert:
        """
        Create new session alert
        
        Args:
            session_id: ID of session with issue
            alert_type: Type of alert (overtime, gps_drift, etc.)
            severity: Alert severity level
            message: Alert description
            auto_generated: Whether alert was automatically generated
        
        Returns:
            Created SessionAlert object
        """
        pass
    
    def resolve_alert(self, alert_id: str, admin_id: str, resolution_notes: str) -> bool:
        """
        Resolve session alert
        
        Args:
            alert_id: ID of alert to resolve
            admin_id: ID of admin resolving alert
            resolution_notes: Notes about resolution
        
        Returns:
            True if resolution successful
        """
        pass
    
    def escalate_alert(self, alert_id: str, new_severity: AlertSeverity, admin_id: str) -> bool:
        """
        Escalate alert severity level
        
        Args:
            alert_id: ID of alert to escalate
            new_severity: New severity level
            admin_id: ID of admin escalating
        
        Returns:
            True if escalation successful
        """
        pass
    
    def get_active_alerts(self, severity_filter: AlertSeverity = None, session_id: str = None) -> List[SessionAlert]:
        """
        Get all active alerts, optionally filtered
        
        Args:
            severity_filter: Optional filter by severity level
            session_id: Optional filter by specific session
        
        Returns:
            List of active SessionAlert objects
        """
        pass
    
    def send_alert_notifications(self, alert: SessionAlert, escalate_to_emergency: bool = False) -> None:
        """
        Send notifications for session alert
        
        Args:
            alert: SessionAlert object
            escalate_to_emergency: Whether to escalate to emergency contacts
        """
        pass
    
    def get_monitoring_dashboard_data(self) -> Dict[str, Union[int, List[Dict], Dict]]:
        """
        Get data for session monitoring dashboard
        
        Returns:
            Dictionary with dashboard metrics and alerts
        """
        pass


class GeolocationService:
    """Service for handling GPS and location verification"""
    
    def __init__(self, maps_api_key: str, geocoding_service):
        self.verification_radius_meters: float = 50.0
        self.location_history_retention_days: int = 90
        self.accuracy_threshold_meters: float = 10.0
        self.maps_api_key = maps_api_key
    
    def verify_location(self, user_location: GPSLocation, target_location: GPSLocation, allowed_radius: float = None) -> LocationValidationResult:
        """
        Verify if user is at target location within acceptable radius
        
        Args:
            user_location: User's current GPS location
            target_location: Expected target location
            allowed_radius: Custom radius in meters (optional)
        
        Returns:
            LocationValidationResult with verification details
        """
        pass
    
    def calculate_distance(self, location1: GPSLocation, location2: GPSLocation) -> float:
        """
        Calculate distance between two GPS locations using Haversine formula
        
        Args:
            location1: First GPS location
            location2: Second GPS location
        
        Returns:
            Distance in meters
        """
        pass
    
    def geocode_address(self, address: str) -> Optional[GPSLocation]:
        """
        Convert address to GPS coordinates
        
        Args:
            address: Street address to geocode
        
        Returns:
            GPSLocation object if successful, None otherwise
        """
        pass
    
    def reverse_geocode(self, location: GPSLocation) -> Optional[str]:
        """
        Convert GPS coordinates to address
        
        Args:
            location: GPS location to reverse geocode
        
        Returns:
            Address string if successful, None otherwise
        """
        pass
    
    def track_location_history(self, user_id: str, session_id: str, location: GPSLocation) -> None:
        """
        Track location history for session
        
        Args:
            user_id: ID of user
            session_id: ID of active session
            location: Current GPS location
        """
        pass
    
    def detect_location_spoofing(self, user_id: str, location: GPSLocation, previous_locations: List[GPSLocation] = None) -> bool:
        """
        Detect potential GPS spoofing attempts
        
        Args:
            user_id: ID of user
            location: Current GPS location
            previous_locations: Recent location history for comparison
        
        Returns:
            True if spoofing suspected, False otherwise
        """
        pass
    
    def get_nearby_seniors(self, student_location: GPSLocation, radius_miles: float = 10.0, service_type: SessionType = None) -> List[str]:
        """
        Find seniors within radius of student location
        
        Args:
            student_location: Student's GPS location
            radius_miles: Search radius in miles
            service_type: Optional filter by service type
        
        Returns:
            List of senior IDs within radius
        """
        pass
    
    def validate_gps_accuracy(self, location: GPSLocation) -> bool:
        """
        Validate GPS location accuracy is acceptable
        
        Args:
            location: GPS location to validate
        
        Returns:
            True if accuracy is acceptable, False otherwise
        """
        pass
    
    def cleanup_old_location_data(self) -> int:
        """
        Clean up old location tracking data based on retention policy
        
        Returns:
            Number of records cleaned up
        """
        pass
    
    def get_location_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Union[int, float]]:
        """
        Get location tracking analytics
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            Dictionary with location tracking metrics
        """
        pass