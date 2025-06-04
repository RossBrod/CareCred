from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    SYSTEM = "system"
    SESSION_UPDATE = "session_update"
    EMERGENCY = "emergency"


class MessageStatus(Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ConversationType(Enum):
    STUDENT_SENIOR = "student_senior"
    STUDENT_ADMIN = "student_admin"
    SENIOR_ADMIN = "senior_admin"
    ADMIN_ADMIN = "admin_admin"


class Conversation:
    """Conversation thread model"""
    
    def __init__(self):
        self.conversation_id: str = None
        self.conversation_type: ConversationType = None
        self.participants: List[str] = []  # user_ids
        self.session_id: Optional[str] = None  # if related to a specific session
        self.subject: str = None
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.last_message_at: datetime = None
        self.is_active: bool = True
        self.is_archived: bool = False
        
        # Emergency/priority settings
        self.priority_level: str = "normal"  # normal, high, urgent, emergency
        self.requires_admin_attention: bool = False
    
    def add_participant(self, user_id: str) -> None:
        pass
    
    def remove_participant(self, user_id: str) -> None:
        pass
    
    def archive_conversation(self) -> None:
        pass
    
    def mark_as_urgent(self, admin_id: str) -> None:
        pass
    
    def get_unread_count(self, user_id: str) -> int:
        pass


class Message:
    """Individual message model"""
    
    def __init__(self):
        self.message_id: str = None
        self.conversation_id: str = None
        self.sender_id: str = None
        self.message_type: MessageType = MessageType.TEXT
        self.content: str = None
        self.attachment_url: Optional[str] = None
        self.attachment_type: Optional[str] = None
        self.status: MessageStatus = MessageStatus.SENT
        self.sent_at: datetime = None
        self.delivered_at: Optional[datetime] = None
        self.read_at: Optional[datetime] = None
        
        # System/automated message fields
        self.is_system_message: bool = False
        self.system_event_type: Optional[str] = None
        self.related_session_id: Optional[str] = None
        
        # Emergency/flagging
        self.is_flagged: bool = False
        self.flag_reason: Optional[str] = None
        self.flagged_by: Optional[str] = None
        self.flagged_at: Optional[datetime] = None
    
    def mark_as_read(self, user_id: str) -> None:
        pass
    
    def flag_message(self, reason: str, flagged_by: str) -> None:
        pass
    
    def unflag_message(self, admin_id: str) -> None:
        pass
    
    def encrypt_content(self) -> None:
        pass
    
    def decrypt_content(self) -> str:
        pass


class NotificationPreferences:
    """User notification preferences model"""
    
    def __init__(self):
        self.user_id: str = None
        self.email_notifications: bool = True
        self.sms_notifications: bool = False
        self.push_notifications: bool = True
        self.in_app_notifications: bool = True
        
        # Specific notification types
        self.session_reminders: bool = True
        self.session_updates: bool = True
        self.new_messages: bool = True
        self.credit_updates: bool = True
        self.admin_announcements: bool = True
        self.emergency_alerts: bool = True
        
        # Timing preferences
        self.quiet_hours_start: str = "22:00"
        self.quiet_hours_end: str = "08:00"
        self.timezone: str = "UTC"
        
        self.updated_at: datetime = None
    
    def update_preferences(self, preferences: Dict) -> None:
        pass
    
    def should_send_notification(self, notification_type: str, current_time: datetime) -> bool:
        pass


class Notification:
    """System notification model"""
    
    def __init__(self):
        self.notification_id: str = None
        self.user_id: str = None
        self.title: str = None
        self.message: str = None
        self.notification_type: str = None
        self.priority: str = "normal"  # low, normal, high, urgent
        self.related_entity_type: Optional[str] = None  # session, message, credit, etc.
        self.related_entity_id: Optional[str] = None
        self.action_url: Optional[str] = None
        self.action_text: Optional[str] = None
        
        # Status tracking
        self.is_read: bool = False
        self.is_sent: bool = False
        self.sent_via: List[str] = []  # email, sms, push, in_app
        self.created_at: datetime = None
        self.sent_at: Optional[datetime] = None
        self.read_at: Optional[datetime] = None
        
        # Delivery tracking
        self.email_delivered: bool = False
        self.sms_delivered: bool = False
        self.push_delivered: bool = False
    
    def mark_as_read(self) -> None:
        pass
    
    def send_notification(self, methods: List[str]) -> None:
        pass
    
    def retry_failed_delivery(self) -> None:
        pass


class EmergencyAlert:
    """Emergency alert system model"""
    
    def __init__(self):
        self.alert_id: str = None
        self.initiated_by: str = None  # user_id
        self.alert_type: str = None    # medical, safety, technical, other
        self.severity: str = "high"    # medium, high, critical
        self.location: Optional[str] = None
        self.session_id: Optional[str] = None
        self.message: str = None
        self.emergency_contacts_notified: List[str] = []
        self.admin_responders: List[str] = []
        
        # Status tracking
        self.is_active: bool = True
        self.is_resolved: bool = False
        self.created_at: datetime = None
        self.resolved_at: Optional[datetime] = None
        self.resolved_by: Optional[str] = None
        self.resolution_notes: Optional[str] = None
    
    def escalate_alert(self, new_severity: str) -> None:
        pass
    
    def assign_responder(self, admin_id: str) -> None:
        pass
    
    def resolve_alert(self, admin_id: str, resolution_notes: str) -> None:
        pass
    
    def notify_emergency_contacts(self) -> None:
        pass