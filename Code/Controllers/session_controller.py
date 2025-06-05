from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from ..Models.session import SessionStatus, SessionType
from ..Models.user import BaseUser, Student, Senior
from ..Services.session_service import SessionService, SessionMatchingService, SessionMonitoringService
from .schemas import (
    SessionRequestCreate, SessionRequestResponse, SessionSchedule, SessionCheckIn,
    SessionCheckOut, SessionRating, SessionCancel, SessionReschedule,
    SessionResponse, PaginatedResponse, APIResponse
)
from .dependencies import (
    get_current_user, get_current_student_user, get_current_senior_user,
    get_pagination
)


router = APIRouter()

def get_session_service() -> SessionService:
    return SessionService()

def get_matching_service() -> SessionMatchingService:
    return SessionMatchingService()

def get_monitoring_service() -> SessionMonitoringService:
    return SessionMonitoringService()


@router.post("/request",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create session request",
            description="Create a new session request (student to senior)")
async def create_session_request(
    request_data: SessionRequestCreate,
    current_student: Student = Depends(get_current_student_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Create a new session request from student to senior."""
    try:
        session_id = await session_service.create_session_request(
            student_id=current_student.user_id,
            senior_id=request_data.senior_id,
            session_type=request_data.session_type,
            preferred_date=request_data.preferred_date,
            preferred_time_start=request_data.preferred_time_start,
            preferred_time_end=request_data.preferred_time_end,
            message=request_data.message
        )
        
        return APIResponse(
            success=True,
            message=f"Session request created successfully. Session ID: {session_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session request"
        )


@router.post("/{session_id}/respond",
             response_model=APIResponse,
             summary="Respond to session request",
             description="Accept or decline a session request (senior only)")
async def respond_to_session_request(
    session_id: str,
    response_data: SessionRequestResponse,
    current_senior: Senior = Depends(get_current_senior_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Respond to a session request (accept/decline)."""
    try:
        success = await session_service.respond_to_session_request(
            session_id=session_id,
            senior_id=current_senior.user_id,
            approved=response_data.approved,
            response_message=response_data.response_message
        )
        
        if success:
            status_msg = "accepted" if response_data.approved else "declined"
            return APIResponse(
                success=True,
                message=f"Session request {status_msg} successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to respond to session request"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to respond to session request"
        )


@router.post("/{session_id}/schedule",
             response_model=APIResponse,
             summary="Schedule session",
             description="Finalize session scheduling after acceptance")
async def schedule_session(
    session_id: str,
    schedule_data: SessionSchedule,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Finalize session scheduling."""
    try:
        success = await session_service.schedule_session(
            session_id=session_id,
            user_id=current_user.user_id,
            scheduled_start_time=schedule_data.scheduled_start_time,
            scheduled_end_time=schedule_data.scheduled_end_time,
            estimated_duration_hours=schedule_data.estimated_duration_hours,
            special_instructions=schedule_data.special_instructions
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Session scheduled successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to schedule session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule session"
        )


@router.post("/{session_id}/checkin",
             response_model=APIResponse,
             summary="Check in to session",
             description="Check in to session with GPS verification")
async def check_in_to_session(
    session_id: str,
    checkin_data: SessionCheckIn,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Check in to session with location verification."""
    try:
        success = await session_service.check_in_to_session(
            session_id=session_id,
            user_id=current_user.user_id,
            location=checkin_data.location.dict()
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Checked in to session successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to check in to session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Check-in failed"
        )


@router.post("/{session_id}/checkout",
             response_model=APIResponse,
             summary="Check out of session",
             description="Check out of session with completion notes")
async def check_out_of_session(
    session_id: str,
    checkout_data: SessionCheckOut,
    background_tasks: BackgroundTasks,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Check out of session and finalize completion."""
    try:
        success = await session_service.check_out_of_session(
            session_id=session_id,
            user_id=current_user.user_id,
            location=checkout_data.location.dict(),
            session_notes=checkout_data.session_notes
        )
        
        if success:
            # Trigger blockchain logging in background
            background_tasks.add_task(
                session_service.initiate_blockchain_logging,
                session_id
            )
            
            return APIResponse(
                success=True,
                message="Checked out of session successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to check out of session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Check-out failed"
        )


@router.post("/{session_id}/rate",
             response_model=APIResponse,
             summary="Rate session",
             description="Submit rating and review for completed session")
async def rate_session(
    session_id: str,
    rating_data: SessionRating,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Submit rating and review for session."""
    try:
        success = await session_service.rate_session(
            session_id=session_id,
            user_id=current_user.user_id,
            rating=rating_data.rating,
            review=rating_data.review,
            rating_categories=rating_data.rating_categories
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Session rated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to rate session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session rating failed"
        )


@router.post("/{session_id}/cancel",
             response_model=APIResponse,
             summary="Cancel session",
             description="Cancel a scheduled session")
async def cancel_session(
    session_id: str,
    cancel_data: SessionCancel,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Cancel a session."""
    try:
        success = await session_service.cancel_session(
            session_id=session_id,
            user_id=current_user.user_id,
            reason=cancel_data.reason
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Session cancelled successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session cancellation failed"
        )


@router.post("/{session_id}/reschedule",
             response_model=APIResponse,
             summary="Reschedule session",
             description="Request to reschedule a session")
async def reschedule_session(
    session_id: str,
    reschedule_data: SessionReschedule,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Reschedule a session."""
    try:
        success = await session_service.reschedule_session(
            session_id=session_id,
            user_id=current_user.user_id,
            new_datetime=reschedule_data.new_datetime,
            reason=reschedule_data.reason
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Session reschedule requested successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reschedule session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session rescheduling failed"
        )


@router.get("/my-sessions",
           response_model=PaginatedResponse,
           summary="Get user's sessions",
           description="Get sessions for current user (as student or senior)")
async def get_user_sessions(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    status_filter: Optional[SessionStatus] = Query(None, description="Filter by session status"),
    session_type: Optional[SessionType] = Query(None, description="Filter by session type"),
    date_from: Optional[datetime] = Query(None, description="Filter sessions from date"),
    date_to: Optional[datetime] = Query(None, description="Filter sessions to date"),
    session_service: SessionService = Depends(get_session_service)
):
    """Get sessions for current user."""
    try:
        filters = {}
        if status_filter:
            filters['status'] = status_filter
        if session_type:
            filters['session_type'] = session_type
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        result = await session_service.get_user_sessions(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.sessions,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.get("/{session_id}",
           response_model=SessionResponse,
           summary="Get session details",
           description="Get detailed information about a specific session")
async def get_session_details(
    session_id: str,
    current_user: BaseUser = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get detailed session information."""
    try:
        session = await session_service.get_session_by_id(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return SessionResponse(
            session_id=session.session_id,
            student_id=session.student_id,
            senior_id=session.senior_id,
            session_type=session.session_type,
            status=session.status,
            title=session.title,
            description=session.description,
            scheduled_start_time=session.scheduled_start_time,
            scheduled_end_time=session.scheduled_end_time,
            actual_duration_hours=session.actual_duration_hours,
            credit_amount=session.credit_amount,
            created_at=session.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session details"
        )


@router.get("/matching/recommendations",
           response_model=List[Dict[str, Any]],
           summary="Get session recommendations",
           description="Get recommended sessions or users for matching")
async def get_session_recommendations(
    current_user: BaseUser = Depends(get_current_user),
    limit: int = Query(10, le=50, description="Number of recommendations"),
    matching_service: SessionMatchingService = Depends(get_matching_service)
):
    """Get personalized session recommendations."""
    try:
        recommendations = await matching_service.get_session_recommendations(
            user_id=current_user.user_id,
            user_type=current_user.get_user_type(),
            limit=limit
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


@router.get("/{session_id}/monitoring",
           response_model=Dict[str, Any],
           summary="Get session monitoring data",
           description="Get real-time monitoring data for active session")
async def get_session_monitoring(
    session_id: str,
    current_user: BaseUser = Depends(get_current_user),
    monitoring_service: SessionMonitoringService = Depends(get_monitoring_service)
):
    """Get real-time session monitoring data."""
    try:
        monitoring_data = await monitoring_service.get_session_monitoring_data(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not monitoring_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or not authorized"
            )
        
        return monitoring_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring data"
        )


@router.get("/analytics/summary",
           response_model=Dict[str, Any],
           summary="Get session analytics",
           description="Get session analytics and statistics for current user")
async def get_session_analytics(
    current_user: BaseUser = Depends(get_current_user),
    date_from: Optional[datetime] = Query(None, description="Analytics from date"),
    date_to: Optional[datetime] = Query(None, description="Analytics to date"),
    session_service: SessionService = Depends(get_session_service)
):
    """Get session analytics and statistics."""
    try:
        analytics = await session_service.get_user_session_analytics(
            user_id=current_user.user_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session analytics"
        )


# Export the router
session_router = router