from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Models.user import BaseUser, Student, Admin
from ..Models.credit import CreditTransactionType, DisbursementType
from ..Services.credit_service import CreditService, InstitutionIntegrationService
from .schemas import (
    CreditAccountCreate, DisbursementRequest, DisbursementApproval,
    CreditAdjustment, DisbursementPreferencesUpdate, CreditAccountResponse,
    TransactionResponse, PaginatedResponse, APIResponse
)
from .dependencies import (
    get_current_user, get_current_student_user, get_current_admin_user,
    get_pagination
)


router = APIRouter()

def get_credit_service() -> CreditService:
    return CreditService()

def get_institution_service() -> InstitutionIntegrationService:
    return InstitutionIntegrationService()


@router.get("/account",
           response_model=CreditAccountResponse,
           summary="Get credit account",
           description="Get current user's credit account information")
async def get_credit_account(
    current_user: BaseUser = Depends(get_current_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get current user's credit account details."""
    try:
        account = await credit_service.get_credit_account(current_user.user_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit account not found"
            )
        
        return CreditAccountResponse(
            account_id=account.account_id,
            student_id=account.student_id,
            total_credits_earned=account.total_credits_earned,
            total_credits_disbursed=account.total_credits_disbursed,
            available_balance=account.available_balance,
            institution_name=account.institution_name,
            created_at=account.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit account"
        )


@router.post("/account",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create credit account",
            description="Create new credit account for student")
async def create_credit_account(
    account_data: CreditAccountCreate,
    current_student: Student = Depends(get_current_student_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Create a new credit account for student."""
    try:
        account_id = await credit_service.create_credit_account(
            student_id=current_student.user_id,
            institution_name=account_data.institution_name,
            institution_account_number=account_data.institution_account_number,
            institution_routing_number=account_data.institution_routing_number
        )
        
        return APIResponse(
            success=True,
            message=f"Credit account created successfully. Account ID: {account_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credit account"
        )


@router.get("/transactions",
           response_model=PaginatedResponse,
           summary="Get credit transactions",
           description="Get credit transaction history for current user")
async def get_credit_transactions(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    transaction_type: Optional[CreditTransactionType] = Query(None, description="Filter by transaction type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get credit transaction history."""
    try:
        filters = {}
        if transaction_type:
            filters['transaction_type'] = transaction_type
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        result = await credit_service.get_credit_transactions(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.transactions,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.post("/disbursement/request",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Request credit disbursement",
            description="Request disbursement of credits to institution")
async def request_credit_disbursement(
    disbursement_data: DisbursementRequest,
    current_student: Student = Depends(get_current_student_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Request disbursement of credits to educational institution."""
    try:
        disbursement_id = await credit_service.request_credit_disbursement(
            student_id=current_student.user_id,
            amount=disbursement_data.amount,
            disbursement_type=disbursement_data.disbursement_type,
            allocation_preferences=disbursement_data.allocation_preferences
        )
        
        return APIResponse(
            success=True,
            message=f"Disbursement request submitted. Request ID: {disbursement_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request disbursement"
        )


@router.get("/disbursements",
           response_model=PaginatedResponse,
           summary="Get disbursement history",
           description="Get disbursement history for current user")
async def get_disbursement_history(
    current_user: BaseUser = Depends(get_current_user),
    pagination: Dict = Depends(get_pagination),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get disbursement history."""
    try:
        filters = {}
        if status_filter:
            filters['status'] = status_filter
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        result = await credit_service.get_disbursement_history(
            user_id=current_user.user_id,
            filters=filters,
            limit=pagination['limit'],
            offset=pagination['offset']
        )
        
        return PaginatedResponse(
            items=result.disbursements,
            total=result.total,
            page=pagination['page'],
            limit=pagination['limit'],
            has_next=result.has_next,
            has_prev=pagination['page'] > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve disbursement history"
        )


@router.get("/disbursements/{disbursement_id}",
           response_model=Dict[str, Any],
           summary="Get disbursement details",
           description="Get detailed information about a specific disbursement")
async def get_disbursement_details(
    disbursement_id: str,
    current_user: BaseUser = Depends(get_current_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get detailed disbursement information."""
    try:
        disbursement = await credit_service.get_disbursement_by_id(
            disbursement_id=disbursement_id,
            user_id=current_user.user_id
        )
        
        if not disbursement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Disbursement not found"
            )
        
        return disbursement
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve disbursement details"
        )


@router.put("/disbursement-preferences",
           response_model=APIResponse,
           summary="Update disbursement preferences",
           description="Update default disbursement allocation preferences")
async def update_disbursement_preferences(
    preferences_data: DisbursementPreferencesUpdate,
    current_student: Student = Depends(get_current_student_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Update disbursement allocation preferences."""
    try:
        success = await credit_service.update_disbursement_preferences(
            student_id=current_student.user_id,
            preferences=preferences_data.preferences
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Disbursement preferences updated successfully"
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
            detail="Failed to update disbursement preferences"
        )


@router.get("/analytics",
           response_model=Dict[str, Any],
           summary="Get credit analytics",
           description="Get credit earning and spending analytics")
async def get_credit_analytics(
    current_user: BaseUser = Depends(get_current_user),
    date_from: Optional[datetime] = Query(None, description="Analytics from date"),
    date_to: Optional[datetime] = Query(None, description="Analytics to date"),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get credit analytics and statistics."""
    try:
        analytics = await credit_service.get_credit_analytics(
            user_id=current_user.user_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get credit analytics"
        )


@router.get("/institutions",
           response_model=List[Dict[str, Any]],
           summary="Get supported institutions",
           description="Get list of supported educational institutions")
async def get_supported_institutions(
    search: Optional[str] = Query(None, description="Search institutions by name"),
    institution_service: InstitutionIntegrationService = Depends(get_institution_service)
):
    """Get list of supported educational institutions."""
    try:
        institutions = await institution_service.get_supported_institutions(search=search)
        return institutions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve institutions"
        )


@router.get("/institutions/{institution_id}/integration-status",
           response_model=Dict[str, Any],
           summary="Get institution integration status",
           description="Get integration status and capabilities for specific institution")
async def get_institution_integration_status(
    institution_id: str,
    current_user: BaseUser = Depends(get_current_user),
    institution_service: InstitutionIntegrationService = Depends(get_institution_service)
):
    """Get institution integration status."""
    try:
        status_info = await institution_service.get_institution_integration_status(
            institution_id=institution_id,
            user_id=current_user.user_id
        )
        
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get integration status"
        )


# Admin-only endpoints
@router.post("/admin/adjustment",
            response_model=APIResponse,
            summary="Make credit adjustment (Admin)",
            description="Make manual credit adjustment for a user account")
async def make_credit_adjustment(
    user_id: str,
    adjustment_data: CreditAdjustment,
    current_admin: Admin = Depends(get_current_admin_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Make manual credit adjustment (admin only)."""
    try:
        adjustment_id = await credit_service.make_credit_adjustment(
            user_id=user_id,
            admin_id=current_admin.user_id,
            amount=adjustment_data.amount,
            reason=adjustment_data.reason,
            adjustment_type=adjustment_data.adjustment_type
        )
        
        return APIResponse(
            success=True,
            message=f"Credit adjustment made successfully. Adjustment ID: {adjustment_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make credit adjustment"
        )


@router.post("/admin/disbursements/{disbursement_id}/approve",
            response_model=APIResponse,
            summary="Approve disbursement (Admin)",
            description="Approve or deny a pending disbursement request")
async def approve_disbursement(
    disbursement_id: str,
    approval_data: DisbursementApproval,
    current_admin: Admin = Depends(get_current_admin_user),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Approve or deny disbursement request (admin only)."""
    try:
        success = await credit_service.approve_disbursement(
            disbursement_id=disbursement_id,
            admin_id=current_admin.user_id,
            approved=approval_data.approved,
            notes=approval_data.notes
        )
        
        if success:
            status_msg = "approved" if approval_data.approved else "denied"
            return APIResponse(
                success=True,
                message=f"Disbursement {status_msg} successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process disbursement approval"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve disbursement"
        )


@router.get("/admin/analytics/system",
           response_model=Dict[str, Any],
           summary="Get system credit analytics (Admin)",
           description="Get system-wide credit analytics and statistics")
async def get_system_credit_analytics(
    current_admin: Admin = Depends(get_current_admin_user),
    date_from: Optional[datetime] = Query(None, description="Analytics from date"),
    date_to: Optional[datetime] = Query(None, description="Analytics to date"),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get system-wide credit analytics (admin only)."""
    try:
        analytics = await credit_service.get_system_credit_analytics(
            admin_id=current_admin.user_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system analytics"
        )


# Export the router
credit_router = router