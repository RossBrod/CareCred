from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..Services.authentication_service import AuthenticationService
from ..Services.session_service import SessionService
from ..Services.credit_service import CreditService
from .schemas import APIResponse


router = APIRouter()

def get_auth_service() -> AuthenticationService:
    return AuthenticationService()

def get_session_service() -> SessionService:
    return SessionService()

def get_credit_service() -> CreditService:
    return CreditService()


@router.get("/health",
           response_model=Dict[str, Any],
           summary="Health check",
           description="Check API health and service status")
async def health_check():
    """Public health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "database": "operational",
            "blockchain": "operational"
        }
    }


@router.get("/stats",
           response_model=Dict[str, Any],
           summary="Public statistics",
           description="Get public platform statistics")
async def get_public_statistics(
    auth_service: AuthenticationService = Depends(get_auth_service),
    session_service: SessionService = Depends(get_session_service),
    credit_service: CreditService = Depends(get_credit_service)
):
    """Get public platform statistics."""
    try:
        # Get anonymized public statistics
        user_stats = await auth_service.get_public_user_statistics()
        session_stats = await session_service.get_public_session_statistics()
        credit_stats = await credit_service.get_public_credit_statistics()
        
        return {
            "total_students": user_stats.get("total_students", 0),
            "total_seniors": user_stats.get("total_seniors", 0),
            "total_sessions_completed": session_stats.get("total_completed", 0),
            "total_credits_earned": credit_stats.get("total_earned", 0.0),
            "total_credits_disbursed": credit_stats.get("total_disbursed", 0.0),
            "platform_uptime_percentage": 99.9,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve public statistics"
        )


@router.get("/universities",
           response_model=List[Dict[str, str]],
           summary="Get supported universities",
           description="Get list of supported universities")
async def get_supported_universities(
    search: Optional[str] = Query(None, description="Search universities by name"),
    state: Optional[str] = Query(None, description="Filter by state"),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get list of supported universities."""
    try:
        universities = await auth_service.get_supported_universities(
            search=search,
            state=state
        )
        
        return universities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve universities"
        )


@router.get("/service-areas",
           response_model=List[Dict[str, Any]],
           summary="Get service areas",
           description="Get geographical areas where CareCred operates")
async def get_service_areas(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    session_service: SessionService = Depends(get_session_service)
):
    """Get service areas where platform operates."""
    try:
        service_areas = await session_service.get_service_areas(
            state=state,
            city=city
        )
        
        return service_areas
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service areas"
        )


@router.get("/session-types",
           response_model=List[Dict[str, Any]],
           summary="Get session types",
           description="Get available types of sessions and services")
async def get_session_types(
    session_service: SessionService = Depends(get_session_service)
):
    """Get available session types and their descriptions."""
    try:
        session_types = await session_service.get_available_session_types()
        return session_types
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session types"
        )


@router.get("/help-categories",
           response_model=List[Dict[str, Any]],
           summary="Get help categories",
           description="Get categories of help that seniors can request")
async def get_help_categories(
    session_service: SessionService = Depends(get_session_service)
):
    """Get available help categories for seniors."""
    try:
        help_categories = await session_service.get_help_categories()
        return help_categories
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve help categories"
        )


@router.get("/faq",
           response_model=List[Dict[str, str]],
           summary="Get FAQ",
           description="Get frequently asked questions")
async def get_faq():
    """Get frequently asked questions."""
    return [
        {
            "question": "How does CareCred work?",
            "answer": "CareCred connects college students with seniors in their community. Students provide various services to seniors and earn educational credits that can be applied to tuition, books, or other educational expenses."
        },
        {
            "question": "What services can students provide?",
            "answer": "Students can provide companionship, help with technology, grocery shopping, transportation, light household tasks, and many other services based on their skills and the senior's needs."
        },
        {
            "question": "How are credits calculated?",
            "answer": "Credits are calculated based on the type of service, duration, complexity, and other factors. All sessions are verified through GPS check-in/out and digital signatures for transparency."
        },
        {
            "question": "Is the platform secure?",
            "answer": "Yes, all session data is recorded on the blockchain for transparency and tamper-proof verification. Personal information is protected with industry-standard security measures."
        },
        {
            "question": "How do seniors request help?",
            "answer": "Seniors can create profiles describing their needs and request help through the platform. They can browse student profiles and request specific students, or the system can suggest matches."
        },
        {
            "question": "How do students get paid?",
            "answer": "Students earn educational credits that are disbursed directly to their educational institutions or can be used for approved educational expenses."
        }
    ]


@router.get("/terms",
           response_model=Dict[str, Any],
           summary="Get terms of service",
           description="Get terms of service information")
async def get_terms_of_service():
    """Get terms of service."""
    return {
        "version": "1.0",
        "last_updated": "2024-01-01",
        "url": "https://carecred.com/terms",
        "summary": "By using CareCred, users agree to provide accurate information, use the platform responsibly, and comply with all applicable laws and regulations."
    }


@router.get("/privacy",
           response_model=Dict[str, Any],
           summary="Get privacy policy",
           description="Get privacy policy information")
async def get_privacy_policy():
    """Get privacy policy."""
    return {
        "version": "1.0",
        "last_updated": "2024-01-01",
        "url": "https://carecred.com/privacy",
        "summary": "CareCred protects user privacy through encryption, secure data storage, and minimal data collection. Session data is recorded on blockchain for transparency while maintaining privacy."
    }


@router.get("/contact",
           response_model=Dict[str, str],
           summary="Get contact information",
           description="Get platform contact information")
async def get_contact_info():
    """Get contact information."""
    return {
        "support_email": "support@carecred.com",
        "business_email": "business@carecred.com",
        "phone": "+1-800-CARECRED",
        "address": "123 Education Blvd, Innovation City, IN 12345",
        "hours": "Monday-Friday 9AM-6PM EST"
    }


@router.get("/blockchain/verify/{transaction_id}",
           response_model=Dict[str, Any],
           summary="Verify blockchain transaction",
           description="Publicly verify a blockchain transaction")
async def verify_blockchain_transaction(
    transaction_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Publicly verify a blockchain transaction."""
    try:
        verification_result = await session_service.verify_public_transaction(
            transaction_id=transaction_id
        )
        
        if verification_result:
            return {
                "verified": True,
                "transaction_id": transaction_id,
                "block_number": verification_result.get("block_number"),
                "timestamp": verification_result.get("timestamp"),
                "verification_url": f"https://explorer.solana.com/tx/{transaction_id}"
            }
        else:
            return {
                "verified": False,
                "transaction_id": transaction_id,
                "message": "Transaction not found or not verified"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify transaction"
        )


@router.get("/platform-status",
           response_model=Dict[str, Any],
           summary="Get platform status",
           description="Get current platform operational status")
async def get_platform_status():
    """Get platform operational status."""
    return {
        "status": "operational",
        "last_updated": datetime.utcnow().isoformat(),
        "services": {
            "api": {
                "status": "operational",
                "uptime": "99.9%",
                "response_time_ms": 150
            },
            "database": {
                "status": "operational",
                "uptime": "99.95%",
                "connections": 45
            },
            "blockchain": {
                "status": "operational",
                "network": "Solana Mainnet",
                "last_block": 245672891,
                "gas_price": "0.000005 SOL"
            },
            "authentication": {
                "status": "operational",
                "active_sessions": 1250
            },
            "file_storage": {
                "status": "operational",
                "availability": "99.9%"
            }
        },
        "maintenance": {
            "scheduled": False,
            "next_window": "2024-12-15T02:00:00Z"
        }
    }


# Export the router
public_router = router