from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from uuid import uuid4


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


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Conversation(BaseModel):
    """Conversation thread model"""
    
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_type: ConversationType
    participants: List[str] = Field(min_items=2, max_items=10)  # user_ids
    session_id: Optional[str] = None  # if related to a specific session
    subject: Optional[str] = Field(None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    is_active: bool = True
    is_archived: bool = False
    
    # Emergency/priority settings
    priority_level: NotificationPriority = NotificationPriority.NORMAL
    requires_admin_attention: bool = False
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('participants')
    def validate_participants(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Duplicate participants not allowed')
        return v
    
    def add_participant(self, user_id: str) -> None:
        """Add participant to conversation"""
        pass
    
    def remove_participant(self, user_id: str) -> None:
        """Remove participant from conversation"""
        pass
    
    def archive_conversation(self) -> None:
        """Archive conversation thread"""
        pass
    
    def mark_as_urgent(self, admin_id: str) -> None:
        """Mark conversation as requiring urgent attention"""
        pass
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread messages for user"""
        pass


class Message(BaseModel):
    """Individual message model"""
    
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str = Field(min_length=1)
    sender_id: str = Field(min_length=1)
    message_type: MessageType = MessageType.TEXT
    content: str = Field(min_length=1, max_length=2000)
    attachment_url: Optional[str] = Field(None, max_length=500)
    attachment_type: Optional[str] = Field(None, max_length=50)
    status: MessageStatus = MessageStatus.SENT
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # System/automated message fields
    is_system_message: bool = False
    system_event_type: Optional[str] = Field(None, max_length=50)
    related_session_id: Optional[str] = None
    
    # Emergency/flagging
    is_flagged: bool = False
    flag_reason: Optional[str] = Field(None, max_length=200)
    flagged_by: Optional[str] = None
    flagged_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('attachment_type')
    def validate_attachment_type(cls, v, values):
        if v and 'attachment_url' not in values:
            raise ValueError('Attachment type requires attachment URL')
        if v:
            allowed_types = ['image', 'document', 'video', 'audio']
            if v not in allowed_types:
                raise ValueError(f'Invalid attachment type: {v}')
        return v
    
    def mark_as_read(self, user_id: str) -> None:
        """Mark message as read by user"""
        pass
    
    def flag_message(self, reason: str, flagged_by: str) -> None:
        """Flag message for review"""
        pass
    
    def unflag_message(self, admin_id: str) -> None:
        """Remove flag from message"""
        pass
    
    def encrypt_content(self) -> None:
        """Encrypt message content for storage"""
        pass
    
    def decrypt_content(self) -> str:
        """Decrypt message content for display"""
        pass


class NotificationPreferences(BaseModel):
    """User notification preferences model"""
    
    user_id: str = Field(min_length=1)
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    in_app_notifications: bool = True
    
    # Specific notification types
    session_reminders: bool = True
    session_updates: bool = True
    new_messages: bool = True
    credit_updates: bool = True
    admin_announcements: bool = True
    emergency_alerts: bool = True
    
    # Timing preferences
    quiet_hours_start: str = Field(default="22:00", regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    quiet_hours_end: str = Field(default="08:00", regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone: str = Field(default="UTC", max_length=50)
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def update_preferences(self, preferences: Dict) -> None:
        """Update notification preferences"""
        pass
    
    def should_send_notification(self, notification_type: str, current_time: datetime) -> bool:
        """Check if notification should be sent based on preferences"""
        pass


class Notification(BaseModel):
    """System notification model"""
    
    notification_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    notification_type: str = Field(min_length=1, max_length=50)
    priority: NotificationPriority = NotificationPriority.NORMAL
    related_entity_type: Optional[str] = Field(None, max_length=50)  # session, message, credit, etc.
    related_entity_id: Optional[str] = None
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=100)
    
    # Status tracking
    is_read: bool = False
    is_sent: bool = False
    sent_via: List[NotificationChannel] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Delivery tracking
    email_delivered: bool = False
    sms_delivered: bool = False
    push_delivered: bool = False
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def mark_as_read(self) -> None:
        """Mark notification as read"""
        pass
    
    def send_notification(self, methods: List[NotificationChannel]) -> None:
        """Send notification via specified channels"""
        pass
    
    def retry_failed_delivery(self) -> None:
        """Retry failed notification delivery"""
        pass


class EmergencyAlert(BaseModel):
    """Emergency alert system model"""
    
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    initiated_by: str = Field(min_length=1)  # user_id
    alert_type: str = Field(regex=r'^(medical|safety|technical|other)$')
    severity: NotificationPriority = NotificationPriority.HIGH
    location: Optional[str] = Field(None, max_length=300)
    session_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=1000)
    emergency_contacts_notified: List[str] = Field(default_factory=list)
    admin_responders: List[str] = Field(default_factory=list)
    
    # Status tracking
    is_active: bool = True
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def escalate_alert(self, new_severity: NotificationPriority) -> None:
        """Escalate alert to higher priority level"""
        pass
    
    def assign_responder(self, admin_id: str) -> None:
        """Assign admin responder to emergency"""
        pass
    
    def resolve_alert(self, admin_id: str, resolution_notes: str) -> None:
        """Resolve emergency alert"""
        pass
    
    def notify_emergency_contacts(self) -> None:
        """Send notifications to emergency contacts"""
        pass


class MessageThread(BaseModel):
    """Message thread aggregation model"""
    
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str = Field(min_length=1)
    subject: str = Field(min_length=1, max_length=200)
    participant_count: int = Field(ge=2)
    message_count: int = Field(default=0, ge=0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_pinned: bool = False
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('tags')
    def validate_tags(cls, v):
        for tag in v:
            if len(tag) > 20:
                raise ValueError('Tag length must be <= 20 characters')
        return v
    
    def add_tag(self, tag: str) -> None:
        """Add tag to message thread"""
        pass
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from message thread"""
        pass
    
    def pin_thread(self) -> None:
        """Pin thread for priority visibility"""
        pass