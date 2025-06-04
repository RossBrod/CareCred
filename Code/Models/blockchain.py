from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"


class SignatureStatus(str, Enum):
    PENDING = "pending"
    COLLECTED = "collected"
    EXPIRED = "expired"


class TaskType(str, Enum):
    COMPANIONSHIP = "companionship"
    TRANSPORTATION = "transportation"
    TECHNOLOGY_HELP = "technology_help"
    HOUSEHOLD_TASKS = "household_tasks"
    MEDICATION_REMINDER = "medication_reminder"
    OTHER = "other"


class SessionLog(BaseModel):
    session_id: UUID
    student_id_hash: str = Field(..., description="Hashed student ID for privacy")
    senior_id_hash: str = Field(..., description="Hashed senior ID for privacy")
    start_time: datetime
    end_time: datetime
    duration: int = Field(..., description="Duration in minutes")
    location_hash: str = Field(..., description="Hashed location data for privacy")
    task_type: TaskType
    student_signature: str = Field(..., description="Student's digital signature")
    senior_signature: str = Field(..., description="Senior's digital signature")
    session_hash: str = Field(..., description="Unique hash of session data")
    credit_amount: float = Field(..., description="Credits earned for this session")
    verification_level: str = Field(default="standard", description="Level of verification applied")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional session metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class BlockchainTransaction(BaseModel):
    transaction_id: str = Field(..., description="Solana transaction signature")
    block_hash: str = Field(..., description="Block hash where transaction is recorded")
    block_number: int = Field(..., description="Block number")
    transaction_index: int = Field(..., description="Index within the block")
    from_address: str = Field(..., description="Sender wallet address")
    to_address: str = Field(..., description="Recipient wallet address")
    gas_used: int = Field(..., description="Gas consumed by transaction")
    gas_price: float = Field(..., description="Gas price in SOL")
    transaction_fee: float = Field(..., description="Total transaction fee")
    status: TransactionStatus
    timestamp: datetime
    confirmations: int = Field(default=0, description="Number of confirmations")
    session_log: SessionLog
    retry_count: int = Field(default=0, description="Number of retry attempts")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SignatureRequest(BaseModel):
    request_id: UUID
    session_id: UUID
    student_id: UUID
    senior_id: UUID
    session_data_hash: str = Field(..., description="Hash of session data to be signed")
    student_signature: Optional[str] = Field(default=None, description="Student's digital signature")
    senior_signature: Optional[str] = Field(default=None, description="Senior's digital signature")
    student_signed_at: Optional[datetime] = Field(default=None)
    senior_signed_at: Optional[datetime] = Field(default=None)
    status: SignatureStatus = Field(default=SignatureStatus.PENDING)
    expires_at: datetime = Field(..., description="Signature collection deadline")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    notification_sent: bool = Field(default=False, description="Whether notification was sent to participants")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class VerificationResult(BaseModel):
    session_id: UUID
    transaction_id: Optional[str] = Field(default=None, description="Blockchain transaction ID")
    is_verified: bool = Field(..., description="Whether session is verified on blockchain")
    verification_timestamp: datetime
    block_number: Optional[int] = Field(default=None, description="Block number where session is recorded")
    confirmations: int = Field(default=0, description="Number of blockchain confirmations")
    integrity_check: bool = Field(..., description="Whether session data integrity is maintained")
    signatures_valid: bool = Field(..., description="Whether both signatures are valid")
    credit_eligible: bool = Field(..., description="Whether session is eligible for credit payout")
    verification_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed verification information")
    public_proof_url: Optional[str] = Field(default=None, description="URL to public blockchain proof")
    verified_by: str = Field(..., description="Verification service or method used")
    error_details: Optional[List[str]] = Field(default=None, description="Any verification errors encountered")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class BlockchainConfig(BaseModel):
    network: str = Field(default="devnet", description="Solana network (mainnet, testnet, devnet)")
    rpc_endpoint: str = Field(..., description="Solana RPC endpoint URL")
    program_id: str = Field(..., description="Smart contract program ID")
    payer_keypair: str = Field(..., description="Payer wallet keypair path")
    commitment_level: str = Field(default="confirmed", description="Transaction commitment level")
    max_retries: int = Field(default=3, description="Maximum retry attempts for failed transactions")
    timeout_seconds: int = Field(default=30, description="Transaction timeout in seconds")
    gas_limit: int = Field(default=200000, description="Maximum gas limit for transactions")


class SignatureCollectionRequest(BaseModel):
    session_id: UUID
    require_both_signatures: bool = Field(default=True, description="Whether both student and senior signatures are required")
    signature_timeout_hours: int = Field(default=24, description="Hours to wait for signatures")
    send_notifications: bool = Field(default=True, description="Whether to send signature request notifications")
    priority: str = Field(default="normal", description="Priority level for signature collection")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class BlockchainHealthCheck(BaseModel):
    network_status: str = Field(..., description="Network connectivity status")
    rpc_latency_ms: float = Field(..., description="RPC endpoint response time")
    last_block_number: int = Field(..., description="Latest block number")
    last_block_timestamp: datetime = Field(..., description="Latest block timestamp")
    program_status: str = Field(..., description="Smart contract program status")
    wallet_balance: float = Field(..., description="Payer wallet balance in SOL")
    pending_transactions: int = Field(..., description="Number of pending transactions")
    failed_transactions_24h: int = Field(..., description="Failed transactions in last 24 hours")
    average_confirmation_time_ms: float = Field(..., description="Average confirmation time")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }