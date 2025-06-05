from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Models.user import BaseUser
from ..Models.messaging import MessageType, NotificationPriority, ConversationType
from ..Services.messaging_service import MessagingService, NotificationService, EmergencyAlertService
from .schemas import (
    ConversationCreate, MessageCreate, MessageFlag, NotificationPreferencesUpdate,
    EmergencyAlertCreate, ConversationResponse, NotificationResponse,
    PaginatedResponse, APIResponse
)
from .dependencies import get_current_user, get_pagination


router = APIRouter()

def get_messaging_service() -> MessagingService:
    return MessagingService()

def get_notification_service() -> NotificationService:
    return NotificationService()

def get_emergency_service() -> EmergencyAlertService:
    return EmergencyAlertService()


@router.post("/conversations",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create conversation",
            description="Create a new conversation between users")
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Create a new conversation."""
    try:
        # Verify current user is in participants list
        if current_user.user_id not in conversation_data.participants:
            conversation_data.participants.append(current_user.user_id)
        
        conversation_id = await messaging_service.create_conversation(
            participants=conversation_data.participants,
            subject=conversation_data.subject,
            session_id=conversation_data.session_id,
            created_by=current_user.user_id
        )
        
        return APIResponse(
            success=True,
            message=f"Conversation created successfully. ID: {conversation_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations",
           response_model=PaginatedResponse,
           summary="Get user conversations",
           description="Get conversations for current user")
async def get_user_conversations(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    conversation_type: Optional[ConversationType] = Query(None, description="Filter by conversation type"),
    search: Optional[str] = Query(None, description="Search in subject or participant names"),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Get conversations for current user."""
    try:
        filters = {}
        if conversation_type:
            filters['conversation_type'] = conversation_type
        if search:
            filters['search'] = search
        
        result = await messaging_service.get_user_conversations(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.conversations,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/conversations/{conversation_id}",
           response_model=ConversationResponse,
           summary="Get conversation details",
           description="Get detailed information about a specific conversation")
async def get_conversation_details(
    conversation_id: str,
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Get conversation details."""
    try:
        conversation = await messaging_service.get_conversation_by_id(
            conversation_id=conversation_id,
            user_id=current_user.user_id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            conversation_type=conversation.conversation_type,
            participants=conversation.participants,
            subject=conversation.subject,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.post("/conversations/{conversation_id}/messages",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Send message",
            description="Send a message in a conversation")
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Send a message in a conversation."""
    try:
        message_id = await messaging_service.send_message(
            conversation_id=conversation_id,
            sender_id=current_user.user_id,
            content=message_data.content,
            message_type=message_data.message_type,
            attachment_url=message_data.attachment_url
        )
        
        return APIResponse(
            success=True,
            message=f"Message sent successfully. ID: {message_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/conversations/{conversation_id}/messages",
           response_model=PaginatedResponse,
           summary="Get conversation messages",
           description="Get messages from a conversation")
async def get_conversation_messages(
    conversation_id: str,
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    since: Optional[datetime] = Query(None, description="Get messages since timestamp"),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Get messages from a conversation."""
    try:
        filters = {}
        if since:
            filters['since'] = since
        
        result = await messaging_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.messages,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.post("/conversations/{conversation_id}/messages/{message_id}/flag",
            response_model=APIResponse,
            summary="Flag message",
            description="Flag a message for moderation review")
async def flag_message(
    conversation_id: str,
    message_id: str,
    flag_data: MessageFlag,
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Flag a message for moderation."""
    try:
        success = await messaging_service.flag_message(
            message_id=message_id,
            conversation_id=conversation_id,
            flagged_by=current_user.user_id,
            reason=flag_data.reason
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Message flagged for review"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to flag message"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to flag message"
        )


@router.post("/conversations/{conversation_id}/messages/{message_id}/read",
            response_model=APIResponse,
            summary="Mark message as read",
            description="Mark a message as read")
async def mark_message_read(
    conversation_id: str,
    message_id: str,
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Mark a message as read."""
    try:
        success = await messaging_service.mark_message_read(
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=current_user.user_id
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Message marked as read"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to mark message as read"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark message as read"
        )


@router.post("/messages/attachment",
            response_model=Dict[str, str],
            summary="Upload message attachment",
            description="Upload an attachment for use in messages")
async def upload_message_attachment(
    file: UploadFile = File(...),
    current_user: BaseUser = Depends(get_current_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Upload file attachment for messages."""
    try:
        # Validate file size and type
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size cannot exceed 10MB"
            )
        
        # Upload and get URL
        attachment_url = await messaging_service.upload_attachment(
            file=file,
            uploaded_by=current_user.user_id
        )
        
        return {
            "attachment_url": attachment_url,
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload attachment"
        )


@router.get("/notifications",
           response_model=PaginatedResponse,
           summary="Get notifications",
           description="Get notifications for current user")
async def get_user_notifications(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get notifications for current user."""
    try:
        filters = {}
        if unread_only:
            filters['unread_only'] = True
        if notification_type:
            filters['notification_type'] = notification_type
        
        result = await notification_service.get_user_notifications(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.notifications,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.post("/notifications/{notification_id}/read",
            response_model=APIResponse,
            summary="Mark notification as read",
            description="Mark a notification as read")
async def mark_notification_read(
    notification_id: str,
    current_user: BaseUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as read."""
    try:
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user.user_id
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Notification marked as read"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to mark notification as read"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.post("/notifications/mark-all-read",
            response_model=APIResponse,
            summary="Mark all notifications as read",
            description="Mark all notifications as read for current user")
async def mark_all_notifications_read(
    current_user: BaseUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read."""
    try:
        count = await notification_service.mark_all_notifications_read(
            user_id=current_user.user_id
        )
        
        return APIResponse(
            success=True,
            message=f"Marked {count} notifications as read"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )


@router.get("/notifications/preferences",
           response_model=Dict[str, Any],
           summary="Get notification preferences",
           description="Get notification preferences for current user")
async def get_notification_preferences(
    current_user: BaseUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get user's notification preferences."""
    try:
        preferences = await notification_service.get_notification_preferences(
            user_id=current_user.user_id
        )
        
        return preferences
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification preferences"
        )


@router.put("/notifications/preferences",
           response_model=APIResponse,
           summary="Update notification preferences",
           description="Update notification preferences for current user")
async def update_notification_preferences(
    preferences_data: NotificationPreferencesUpdate,
    current_user: BaseUser = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Update user's notification preferences."""
    try:
        success = await notification_service.update_notification_preferences(
            user_id=current_user.user_id,
            preferences=preferences_data.dict(exclude_unset=True)
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Notification preferences updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.post("/emergency/alert",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create emergency alert",
            description="Create an emergency alert")
async def create_emergency_alert(
    alert_data: EmergencyAlertCreate,
    current_user: BaseUser = Depends(get_current_user),
    emergency_service: EmergencyAlertService = Depends(get_emergency_service)
):
    """Create an emergency alert."""
    try:
        alert_id = await emergency_service.create_emergency_alert(
            user_id=current_user.user_id,
            alert_type=alert_data.alert_type,
            message=alert_data.message,
            location=alert_data.location,
            session_id=alert_data.session_id
        )
        
        return APIResponse(
            success=True,
            message=f"Emergency alert created. Alert ID: {alert_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create emergency alert"
        )


@router.get("/emergency/alerts",
           response_model=PaginatedResponse,
           summary="Get emergency alerts",
           description="Get emergency alerts for current user")
async def get_emergency_alerts(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    emergency_service: EmergencyAlertService = Depends(get_emergency_service)
):
    """Get emergency alerts for current user."""
    try:
        filters = {}
        if alert_type:
            filters['alert_type'] = alert_type
        if status_filter:
            filters['status'] = status_filter
        
        result = await emergency_service.get_user_emergency_alerts(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.alerts,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emergency alerts"
        )


# Export the router
messaging_router = router