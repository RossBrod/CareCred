from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager

from ..Models.blockchain import (
    SessionLog, BlockchainTransaction, SignatureRequest, VerificationResult,
    SignatureCollectionRequest, BlockchainHealthCheck, TransactionStatus
)
from ..Services.blockchain_service import (
    SolanaService, SignatureService, HashingService, BlockchainVerificationService,
    BlockchainError, SignatureError, VerificationError
)
from ..Services.authentication_service import verify_token, get_current_user, require_admin


security = HTTPBearer()
router = APIRouter(prefix="/blockchain", tags=["blockchain"])


class LogSessionRequest(BaseModel):
    session_id: UUID
    student_signature: str
    senior_signature: str
    force_write: bool = False

    class Config:
        json_encoders = {UUID: lambda v: str(v)}


class SignatureCollectionResponse(BaseModel):
    request_id: UUID
    status: str
    expires_at: datetime
    collection_url: str

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class TransactionProofResponse(BaseModel):
    transaction_id: str
    proof_data: Dict[str, Any]
    verification_url: str
    generated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BatchVerificationRequest(BaseModel):
    session_ids: List[UUID]
    include_details: bool = True

    class Config:
        json_encoders = {UUID: lambda v: str(v)}


async def get_blockchain_services():
    """Dependency to get initialized blockchain services."""
    pass


async def verify_blockchain_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enhanced authentication for blockchain operations."""
    pass


async def rate_limit_blockchain_ops(user_id: str):
    """Rate limiting for blockchain operations to prevent abuse."""
    pass


@router.post("/log-session", 
             response_model=BlockchainTransaction,
             status_code=status.HTTP_201_CREATED,
             summary="Log completed session to blockchain",
             description="Write a completed session with dual signatures to Solana blockchain")
async def log_session_to_blockchain(
    request: LogSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Log a completed session to the blockchain with dual signatures.
    
    This endpoint writes session data to Solana blockchain after verifying
    both student and senior signatures. The operation is async and may take
    several seconds to complete due to blockchain confirmation times.
    
    Args:
        request: Session logging request with signatures
        background_tasks: FastAPI background tasks for async operations
        current_user: Authenticated user information
        services: Injected blockchain services
        
    Returns:
        BlockchainTransaction: Transaction details and status
        
    Raises:
        HTTPException: If signatures invalid, session not found, or blockchain error
    """
    try:
        solana_service, signature_service, verification_service = services
        
        # Rate limiting
        await rate_limit_blockchain_ops(current_user["user_id"])
        
        # Verify both signatures before blockchain write
        # Implementation would verify signatures here
        
        # Create session log object
        # Implementation would create SessionLog from request
        
        # Write to blockchain
        # transaction = await solana_service.write_session_to_blockchain(session_log)
        
        # Background verification
        # background_tasks.add_task(verify_transaction_background, transaction.transaction_id)
        
        # Return mock response for now
        return BlockchainTransaction(
            transaction_id="mock_transaction_id",
            block_hash="mock_block_hash",
            block_number=12345,
            transaction_index=0,
            from_address="mock_from_address",
            to_address="mock_to_address",
            gas_used=50000,
            gas_price=0.000005,
            transaction_fee=0.00025,
            status=TransactionStatus.PENDING,
            timestamp=datetime.utcnow(),
            confirmations=0,
            session_log=SessionLog(
                session_id=request.session_id,
                student_id_hash="mock_student_hash",
                senior_id_hash="mock_senior_hash",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                duration=60,
                location_hash="mock_location_hash",
                task_type="companionship",
                student_signature=request.student_signature,
                senior_signature=request.senior_signature,
                session_hash="mock_session_hash",
                credit_amount=10.0
            )
        )
        
    except SignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature: {str(e)}"
        )
    except BlockchainError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Blockchain service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/verify/{session_id}",
            response_model=VerificationResult,
            summary="Verify session on blockchain",
            description="Verify that a session exists on blockchain with valid signatures")
async def verify_session_on_blockchain(
    session_id: UUID,
    include_proof: bool = False,
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Verify that a session exists on blockchain with complete integrity.
    
    Performs comprehensive verification including:
    - Transaction existence on blockchain
    - Signature validity
    - Data integrity
    - Credit eligibility
    
    Args:
        session_id: UUID of session to verify
        include_proof: Whether to include public proof data
        current_user: Authenticated user information
        services: Injected blockchain services
        
    Returns:
        VerificationResult: Complete verification status and details
        
    Raises:
        HTTPException: If session not found or verification fails
    """
    try:
        solana_service, signature_service, verification_service = services
        
        # Perform comprehensive verification
        # result = await verification_service.verify_session_integrity(session_id)
        
        # Mock response for now
        result = VerificationResult(
            session_id=session_id,
            transaction_id="mock_transaction_id",
            is_verified=True,
            verification_timestamp=datetime.utcnow(),
            block_number=12345,
            confirmations=10,
            integrity_check=True,
            signatures_valid=True,
            credit_eligible=True,
            verification_details={"mock": "data"},
            verified_by="BlockchainVerificationService"
        )
        
        if include_proof:
            proof_data = await verification_service.get_public_transaction_proof(result.transaction_id)
            result.verification_details["public_proof"] = proof_data
        
        return result
        
    except VerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification error: {str(e)}"
        )


@router.get("/transactions/{user_hash}",
            response_model=List[SessionLog],
            summary="Get user's blockchain transaction history",
            description="Retrieve all blockchain-verified sessions for a specific user")
async def get_user_blockchain_history(
    user_hash: str,
    limit: int = 100,
    offset: int = 0,
    verified_only: bool = True,
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Get complete blockchain transaction history for a user.
    
    Returns all sessions that have been successfully written to blockchain
    for the specified user. Results are paginated and can be filtered.
    
    Args:
        user_hash: Hashed user ID to get history for
        limit: Maximum number of records to return (default 100)
        offset: Number of records to skip for pagination
        verified_only: Only return fully verified transactions
        current_user: Authenticated user information
        services: Injected blockchain services
        
    Returns:
        List[SessionLog]: List of user's blockchain-verified sessions
        
    Raises:
        HTTPException: If user not authorized or service error
    """
    try:
        solana_service, _, _ = services
        
        # Verify user can access this hash (admin or own data)
        # Implementation would verify access permissions
        
        # Get session logs from blockchain
        # sessions = await solana_service.get_session_logs(user_hash, limit)
        
        # Mock response for now
        sessions = []
        
        # Apply pagination
        start = offset
        end = offset + limit
        return sessions[start:end]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transaction history: {str(e)}"
        )


@router.post("/signatures/collect",
             response_model=SignatureCollectionResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Initiate signature collection",
             description="Start process to collect digital signatures from session participants")
async def collect_session_signatures(
    request: SignatureCollectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Initiate collection of digital signatures from session participants.
    
    Creates a signature collection request and sends notifications to
    both student and senior to digitally sign the session data.
    
    Args:
        request: Signature collection configuration
        background_tasks: FastAPI background tasks for notifications
        current_user: Authenticated user information
        services: Injected blockchain services
        
    Returns:
        SignatureCollectionResponse: Collection request details and status
        
    Raises:
        HTTPException: If session not found or collection fails
    """
    try:
        _, signature_service, _ = services
        
        # Create signature request
        # signature_request = await signature_service.collect_dual_signatures(request)
        
        # Send notifications if requested
        if request.send_notifications:
            # background_tasks.add_task(send_signature_notifications, signature_request)
            pass
        
        # Mock response for now
        return SignatureCollectionResponse(
            request_id=UUID("12345678-1234-5678-9012-123456789012"),
            status="pending",
            expires_at=datetime.utcnow(),
            collection_url="https://app.carecred.com/sign/mock_id"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating signature collection: {str(e)}"
        )


@router.get("/proof/{transaction_id}",
            response_model=TransactionProofResponse,
            summary="Get public transaction proof",
            description="Generate independently verifiable proof of blockchain transaction")
async def get_public_transaction_proof(
    transaction_id: str,
    format: str = "json",
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Generate public proof of blockchain transaction for independent verification.
    
    Creates a cryptographic proof that can be verified by third parties
    without requiring access to private systems or data.
    
    Args:
        transaction_id: Blockchain transaction ID to generate proof for
        format: Proof format (json, pdf, qr)
        current_user: Authenticated user information
        services: Injected blockchain services
        
    Returns:
        TransactionProofResponse: Public proof data and verification URL
        
    Raises:
        HTTPException: If transaction not found or proof generation fails
    """
    try:
        _, _, verification_service = services
        
        # Generate public proof
        # proof_data = await verification_service.get_public_transaction_proof(transaction_id)
        
        # Mock response for now
        proof_data = {
            "transaction_id": transaction_id,
            "block_number": 12345,
            "merkle_proof": "mock_merkle_proof",
            "signature_hashes": ["hash1", "hash2"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        verification_url = f"https://explorer.solana.com/tx/{transaction_id}"
        
        return TransactionProofResponse(
            transaction_id=transaction_id,
            proof_data=proof_data,
            verification_url=verification_url,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating transaction proof: {str(e)}"
        )


@router.post("/verify/batch",
             response_model=List[VerificationResult],
             summary="Batch verify multiple sessions",
             description="Verify multiple sessions on blockchain in a single request")
async def batch_verify_sessions(
    request: BatchVerificationRequest,
    current_user: dict = Depends(require_admin),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Verify multiple sessions on blockchain in batch for efficiency.
    
    Admin-only endpoint for batch verification of sessions.
    Useful for compliance reporting and bulk verification tasks.
    
    Args:
        request: Batch verification request with session IDs
        current_user: Authenticated admin user
        services: Injected blockchain services
        
    Returns:
        List[VerificationResult]: Verification results for all sessions
        
    Raises:
        HTTPException: If not admin or verification fails
    """
    try:
        _, _, verification_service = services
        
        # Perform batch verification
        # results = await verification_service.batch_verify_sessions(request.session_ids)
        
        # Mock response for now
        results = [
            VerificationResult(
                session_id=session_id,
                is_verified=True,
                verification_timestamp=datetime.utcnow(),
                integrity_check=True,
                signatures_valid=True,
                credit_eligible=True,
                verified_by="BatchVerificationService"
            )
            for session_id in request.session_ids
        ]
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch verification error: {str(e)}"
        )


@router.get("/health",
            response_model=BlockchainHealthCheck,
            summary="Check blockchain service health",
            description="Get current status and health metrics of blockchain services")
async def check_blockchain_health(
    current_user: dict = Depends(require_admin),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Check overall health and status of blockchain services.
    
    Admin-only endpoint that provides detailed health metrics
    for monitoring and alerting systems.
    
    Args:
        current_user: Authenticated admin user
        services: Injected blockchain services
        
    Returns:
        BlockchainHealthCheck: Comprehensive health status
    """
    try:
        solana_service, _, _ = services
        
        # Check blockchain health
        # health = await solana_service.check_blockchain_status()
        
        # Mock response for now
        health = BlockchainHealthCheck(
            network_status="healthy",
            rpc_latency_ms=250.5,
            last_block_number=12345678,
            last_block_timestamp=datetime.utcnow(),
            program_status="active",
            wallet_balance=5.25,
            pending_transactions=3,
            failed_transactions_24h=1,
            average_confirmation_time_ms=2500.0
        )
        
        return health
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.post("/signatures/{request_id}/submit",
             response_model=SignatureRequest,
             summary="Submit digital signature",
             description="Submit digital signature for pending signature request")
async def submit_digital_signature(
    request_id: UUID,
    signature: str,
    current_user: dict = Depends(get_current_user),
    services: tuple = Depends(get_blockchain_services)
):
    """
    Submit digital signature for pending signature request.
    
    Allows participants to submit their digital signatures
    for session verification.
    
    Args:
        request_id: Signature request ID
        signature: Digital signature string
        current_user: Authenticated user submitting signature
        services: Injected blockchain services
        
    Returns:
        SignatureRequest: Updated signature request status
    """
    try:
        _, signature_service, _ = services
        
        # Submit signature
        # result = await signature_service.submit_signature(
        #     request_id, current_user["user_id"], signature
        # )
        
        # Mock response for now
        result = SignatureRequest(
            request_id=request_id,
            session_id=UUID("12345678-1234-5678-9012-123456789012"),
            student_id=UUID("12345678-1234-5678-9012-123456789012"),
            senior_id=UUID("12345678-1234-5678-9012-123456789012"),
            session_data_hash="mock_hash",
            student_signature=signature if current_user.get("role") == "student" else None,
            senior_signature=signature if current_user.get("role") == "senior" else None,
            expires_at=datetime.utcnow(),
            status="pending"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting signature: {str(e)}"
        )


async def verify_transaction_background(transaction_id: str):
    """Background task to verify transaction after blockchain write."""
    pass


async def send_signature_notifications(signature_request: SignatureRequest):
    """Background task to send signature collection notifications."""
    pass