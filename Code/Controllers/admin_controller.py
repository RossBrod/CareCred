from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Models.user import Admin, UserType, UserStatus
from ..Models.session import AlertSeverity
from ..Services.authentication_service import AuthenticationService
from ..Services.session_service import SessionService
from ..Services.credit_service import CreditService
from ..Services.messaging_service import MessagingService
from .schemas import (
    UserApproval, AlertResolution, AlertEscalation, BulkStatusUpdate,
    InstitutionCreate, ReportGenerate, PaginatedResponse, APIResponse
)
from .dependencies import get_current_admin_user, get_pagination


router = APIRouter()

def get_auth_service() -> AuthenticationService:
    return AuthenticationService()

def get_session_service() -> SessionService:
    return SessionService()

def get_credit_service() -> CreditService:
    return CreditService()

def get_messaging_service() -> MessagingService:
    return MessagingService()


@router.get("/dashboard/summary",
           response_model=Dict[str, Any],
           summary="Get admin dashboard summary",
           description="Get high-level metrics and statistics for admin dashboard")
async def get_admin_dashboard_summary(
    current_admin: Admin = Depends(get_current_admin_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
    session_service: SessionService = Depends(get_session_service),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get admin dashboard summary with key metrics."""
    try:
        # Get various metrics in parallel
        user_stats = await auth_service.get_user_statistics()
        session_stats = await session_service.get_session_statistics()
        credit_stats = await credit_service.get_credit_statistics()
        
        return {
            "users": user_stats,
            "sessions": session_stats,
            "credits": credit_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )


@router.get("/users/pending-approval",
           response_model=PaginatedResponse,
           summary="Get users pending approval",
           description="Get list of users awaiting admin approval")
async def get_pending_users(
    current_admin: Admin = Depends(get_current_admin_user),
    pagination: Dict = Depends(get_pagination),
    user_type: Optional[UserType] = Query(None, description="Filter by user type"),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get users pending approval."""
    try:
        filters = {"status": UserStatus.PENDING_APPROVAL}
        if user_type:
            filters["user_type"] = user_type
        
        result = await auth_service.get_users_by_filters(
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.users,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending users"
        )


@router.post("/users/{user_id}/approve",
            response_model=APIResponse,
            summary="Approve or deny user",
            description="Approve or deny a user registration")
async def approve_user(
    user_id: str,
    approval_data: UserApproval,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Approve or deny user registration."""
    try:
        success = await auth_service.approve_user_registration(
            user_id=user_id,
            admin_id=current_admin.user_id,
            approved=approval_data.approved,
            notes=approval_data.notes
        )
        
        if success:
            # Send notification in background
            background_tasks.add_task(
                auth_service.send_approval_notification,
                user_id,
                approval_data.approved
            )
            
            status_msg = "approved" if approval_data.approved else "denied"
            return APIResponse(
                success=True,
                message=f"User {status_msg} successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process user approval"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve user"
        )


@router.get("/users",
           response_model=PaginatedResponse,
           summary="Get all users",
           description="Get paginated list of all users with filtering")
async def get_all_users(
    current_admin: Admin = Depends(get_current_admin_user),
    pagination: Dict = Depends(get_pagination),
    user_type: Optional[UserType] = Query(None, description="Filter by user type"),
    status_filter: Optional[UserStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get all users with filtering and pagination."""
    try:
        filters = {}
        if user_type:
            filters["user_type"] = user_type
        if status_filter:
            filters["status"] = status_filter
        if search:
            filters["search"] = search
        
        result = await auth_service.get_users_by_filters(
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.users,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.post("/users/{user_id}/suspend",
            response_model=APIResponse,
            summary="Suspend user",
            description="Suspend a user account")
async def suspend_user(
    user_id: str,
    reason: str,
    current_admin: Admin = Depends(get_current_admin_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Suspend a user account."""
    try:
        success = await auth_service.suspend_user(
            user_id=user_id,
            admin_id=current_admin.user_id,
            reason=reason
        )
        
        if success:
            return APIResponse(
                success=True,
                message="User suspended successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to suspend user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suspend user"
        )


@router.post("/users/{user_id}/reactivate",
            response_model=APIResponse,
            summary="Reactivate user",
            description="Reactivate a suspended user account")
async def reactivate_user(
    user_id: str,
    current_admin: Admin = Depends(get_current_admin_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Reactivate a suspended user account."""
    try:
        success = await auth_service.reactivate_user(
            user_id=user_id,
            admin_id=current_admin.user_id
        )
        
        if success:
            return APIResponse(
                success=True,
                message="User reactivated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reactivate user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate user"
        )


@router.get("/sessions/monitoring",
           response_model=PaginatedResponse,
           summary="Get sessions for monitoring",
           description="Get sessions requiring admin monitoring or attention")
async def get_sessions_for_monitoring(
    current_admin: Admin = Depends(get_current_admin_user),
    pagination: Dict = Depends(get_pagination),
    alert_level: Optional[str] = Query(None, description="Filter by alert level"),
    session_service: SessionService = Depends(get_session_service)
):
    """Get sessions requiring monitoring."""
    try:
        filters = {}
        if alert_level:
            filters["alert_level"] = alert_level
        
        result = await session_service.get_sessions_for_monitoring(
            admin_id=current_admin.user_id,
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
            detail="Failed to retrieve monitoring sessions"
        )


@router.get("/alerts",
           response_model=PaginatedResponse,
           summary="Get system alerts",
           description="Get system alerts requiring admin attention")
async def get_system_alerts(
    current_admin: Admin = Depends(get_current_admin_user),
    pagination: Dict = Depends(get_pagination),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    session_service: SessionService = Depends(get_session_service)
):
    """Get system alerts."""
    try:
        filters = {}
        if severity:
            filters["severity"] = severity
        if resolved is not None:
            filters["resolved"] = resolved
        
        result = await session_service.get_system_alerts(
            admin_id=current_admin.user_id,
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
            detail="Failed to retrieve system alerts"
        )


@router.post("/alerts/{alert_id}/resolve",
            response_model=APIResponse,
            summary="Resolve alert",
            description="Mark an alert as resolved")
async def resolve_alert(
    alert_id: str,
    resolution_data: AlertResolution,
    current_admin: Admin = Depends(get_current_admin_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Resolve a system alert."""
    try:
        success = await session_service.resolve_alert(
            alert_id=alert_id,
            admin_id=current_admin.user_id,
            resolution_notes=resolution_data.resolution_notes
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Alert resolved successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to resolve alert"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert"
        )


@router.post("/alerts/{alert_id}/escalate",
            response_model=APIResponse,
            summary="Escalate alert",
            description="Escalate an alert to higher severity")
async def escalate_alert(
    alert_id: str,
    escalation_data: AlertEscalation,
    current_admin: Admin = Depends(get_current_admin_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Escalate a system alert."""
    try:
        success = await session_service.escalate_alert(
            alert_id=alert_id,
            admin_id=current_admin.user_id,
            new_severity=escalation_data.new_severity
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Alert escalated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to escalate alert"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to escalate alert"
        )


@router.get("/reports/financial",
           response_model=Dict[str, Any],
           summary="Get financial reports",
           description="Get financial and credit reports")
async def get_financial_reports(
    current_admin: Admin = Depends(get_current_admin_user),
    report_type: str = Query("monthly", description="Report type (monthly, quarterly, annual)"),
    date_from: Optional[datetime] = Query(None, description="Report start date"),
    date_to: Optional[datetime] = Query(None, description="Report end date"),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get financial and credit reports."""
    try:
        report = await credit_service.generate_financial_report(
            admin_id=current_admin.user_id,
            report_type=report_type,
            date_from=date_from,
            date_to=date_to
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial report"
        )


@router.post("/reports/generate",
            response_model=APIResponse,
            summary="Generate custom report",
            description="Generate custom report based on parameters")
async def generate_custom_report(
    report_data: ReportGenerate,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Generate custom report."""
    try:
        # Generate report in background
        background_tasks.add_task(
            credit_service.generate_custom_report,
            admin_id=current_admin.user_id,
            report_type=report_data.report_type,
            start_date=report_data.start_date,
            end_date=report_data.end_date,
            institution_id=report_data.institution_id
        )
        
        return APIResponse(
            success=True,
            message="Custom report generation started. You will be notified when complete."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start report generation"
        )


@router.get("/institutions",
           response_model=List[Dict[str, Any]],
           summary="Get institutions",
           description="Get list of integrated institutions")
async def get_institutions(
    current_admin: Admin = Depends(get_current_admin_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get list of integrated institutions."""
    try:
        institutions = await credit_service.get_all_institutions(
            admin_id=current_admin.user_id
        )
        
        return institutions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve institutions"
        )


@router.post("/institutions",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Add institution",
            description="Add new educational institution")
async def add_institution(
    institution_data: InstitutionCreate,
    current_admin: Admin = Depends(get_current_admin_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Add new educational institution."""
    try:
        institution_id = await credit_service.add_institution(
            admin_id=current_admin.user_id,
            institution_data=institution_data.dict()
        )
        
        return APIResponse(
            success=True,
            message=f"Institution added successfully. ID: {institution_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add institution"
        )


@router.get("/flagged-content",
           response_model=PaginatedResponse,
           summary="Get flagged content",
           description="Get content flagged for moderation review")
async def get_flagged_content(
    current_admin: Admin = Depends(get_current_admin_user),
    pagination: Dict = Depends(get_pagination),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Get flagged content for moderation."""
    try:
        filters = {}
        if content_type:
            filters["content_type"] = content_type
        
        result = await messaging_service.get_flagged_content(
            admin_id=current_admin.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.content,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve flagged content"
        )


@router.post("/content/{content_id}/moderate",
            response_model=APIResponse,
            summary="Moderate content",
            description="Take moderation action on flagged content")
async def moderate_content(
    content_id: str,
    action: str,
    reason: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin_user),
    messaging_service: MessagingService = Depends(get_messaging_service)
):
    """Take moderation action on flagged content."""
    try:
        success = await messaging_service.moderate_content(
            content_id=content_id,
            admin_id=current_admin.user_id,
            action=action,
            reason=reason
        )
        
        if success:
            return APIResponse(
                success=True,
                message=f"Moderation action '{action}' applied successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to apply moderation action"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate content"
        )


@router.post("/bulk-actions/update-status",
            response_model=APIResponse,
            summary="Bulk update status",
            description="Update status for multiple items")
async def bulk_update_status(
    update_data: BulkStatusUpdate,
    current_admin: Admin = Depends(get_current_admin_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Bulk update status for multiple items."""
    try:
        result = await auth_service.bulk_update_status(
            admin_id=current_admin.user_id,
            item_ids=update_data.item_ids,
            new_status=update_data.new_status,
            reason=update_data.reason
        )
        
        return APIResponse(
            success=True,
            message=f"Updated {result.updated_count} items successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk update"
        )


# Export the router
admin_router = router