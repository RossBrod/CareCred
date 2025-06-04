from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from uuid import uuid4


class CreditTransactionType(Enum):
    EARNED = "earned"
    DISBURSED = "disbursed"
    ADJUSTED = "adjusted"
    REFUNDED = "refunded"


class CreditTransactionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DisbursementType(Enum):
    TUITION = "tuition"
    HOUSING = "housing"
    BOOKS = "books"
    MEAL_PLAN = "meal_plan"
    MIXED = "mixed"


class PaymentMethod(Enum):
    ACH = "ach"
    WIRE = "wire"
    CHECK = "check"
    DIRECT_API = "direct_api"


class CreditAccount(BaseModel):
    """Student's credit account model"""
    
    account_id: str = Field(default_factory=lambda: str(uuid4()))
    student_id: str = Field(min_length=1)
    total_credits_earned: float = Field(default=0.0, ge=0.0)
    total_credits_disbursed: float = Field(default=0.0, ge=0.0)
    pending_credits: float = Field(default=0.0, ge=0.0)
    available_balance: float = Field(default=0.0, ge=0.0)
    lifetime_earnings: float = Field(default=0.0, ge=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Institution account details
    institution_name: Optional[str] = Field(None, max_length=200)
    institution_account_number: Optional[str] = Field(None, max_length=50)
    institution_routing_number: Optional[str] = Field(None, max_length=20)
    
    # Disbursement preferences
    default_disbursement_split: Dict[str, float] = Field(
        default_factory=lambda: {"tuition": 60.0, "housing": 40.0}
    )
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('default_disbursement_split')
    def validate_disbursement_split(cls, v):
        total = sum(v.values())
        if abs(total - 100.0) > 0.01:  # Allow small floating point errors
            raise ValueError('Disbursement split must total 100%')
        for percentage in v.values():
            if percentage < 0 or percentage > 100:
                raise ValueError('Percentages must be between 0 and 100')
        return v
    
    def get_available_balance(self) -> float:
        """Calculate available balance for disbursement"""
        pass
    
    def add_earned_credits(self, amount: float, session_id: str) -> None:
        """Add earned credits from completed session"""
        pass
    
    def deduct_disbursed_credits(self, amount: float, transaction_id: str) -> None:
        """Deduct credits for disbursement"""
        pass
    
    def update_disbursement_split(self, split_percentages: Dict[str, float]) -> None:
        """Update disbursement allocation preferences"""
        pass
    
    def calculate_disbursement_amounts(self, total_amount: float) -> Dict[str, float]:
        """Calculate disbursement amounts based on preferences"""
        pass


class CreditTransaction(BaseModel):
    """Individual credit transaction model"""
    
    transaction_id: str = Field(default_factory=lambda: str(uuid4()))
    account_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    session_id: Optional[str] = None
    transaction_type: CreditTransactionType
    status: CreditTransactionStatus = CreditTransactionStatus.PENDING
    amount: float = Field(gt=0.0)
    description: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None  # admin_id
    
    # Blockchain verification
    blockchain_hash: Optional[str] = None
    blockchain_verified: bool = False
    
    # Disbursement specific fields
    disbursement_type: Optional[DisbursementType] = None
    institution_reference: Optional[str] = Field(None, max_length=100)
    disbursement_batch_id: Optional[str] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def process_transaction(self, admin_id: str) -> bool:
        """Process pending transaction"""
        pass
    
    def cancel_transaction(self, reason: str, admin_id: str) -> None:
        """Cancel transaction with reason"""
        pass
    
    def verify_on_blockchain(self) -> bool:
        """Verify transaction exists on blockchain"""
        pass


class CreditDisbursement(BaseModel):
    """Credit disbursement to institution model"""
    
    disbursement_id: str = Field(default_factory=lambda: str(uuid4()))
    student_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    institution_name: str = Field(min_length=1, max_length=200)
    disbursement_type: DisbursementType
    amount: float = Field(gt=0.0)
    status: CreditTransactionStatus = CreditTransactionStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    approved_by: Optional[str] = None  # admin_id
    processed_by: Optional[str] = None  # admin_id
    
    # Institution integration
    institution_transaction_id: Optional[str] = Field(None, max_length=100)
    institution_confirmation: Optional[str] = Field(None, max_length=200)
    payment_method: PaymentMethod = PaymentMethod.ACH
    
    # Related transactions
    transaction_ids: List[str] = Field(default_factory=list)
    session_ids: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def approve_disbursement(self, admin_id: str) -> None:
        """Approve disbursement for processing"""
        pass
    
    def process_payment(self, admin_id: str) -> bool:
        """Process approved disbursement payment"""
        pass
    
    def add_transaction(self, transaction_id: str) -> None:
        """Add related transaction to disbursement"""
        pass
    
    def calculate_total_amount(self) -> float:
        """Calculate total disbursement amount"""
        pass


class InstitutionAccount(BaseModel):
    """Model for university/institution account integration"""
    
    institution_id: str = Field(default_factory=lambda: str(uuid4()))
    institution_name: str = Field(min_length=1, max_length=200)
    contact_name: str = Field(min_length=1, max_length=100)
    contact_email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: str = Field(regex=r'^\+?1?\d{9,15}$')
    account_number: Optional[str] = Field(None, max_length=50)
    routing_number: Optional[str] = Field(None, max_length=20)
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key_hash: Optional[str] = Field(None, exclude=True)
    integration_type: str = Field(regex=r'^(direct_api|file_transfer|manual)$')
    is_active: bool = True
    last_sync: Optional[datetime] = None
    total_disbursements: float = Field(default=0.0, ge=0.0)
    pending_disbursements: float = Field(default=0.0, ge=0.0)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def test_connection(self) -> bool:
        """Test connection to institution's systems"""
        pass
    
    def sync_student_data(self) -> List[Dict]:
        """Sync student enrollment data"""
        pass
    
    def process_disbursement(self, disbursement: CreditDisbursement) -> bool:
        """Process disbursement to institution"""
        pass
    
    def get_student_account_info(self, student_id: str) -> Dict:
        """Get student account information from institution"""
        pass


class CreditReport(BaseModel):
    """Model for credit reporting and analytics"""
    
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    report_type: str = Field(regex=r'^(monthly|quarterly|annual|custom)$')
    start_date: datetime
    end_date: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(min_length=1)  # admin_id
    
    # Report data
    total_credits_issued: float = Field(ge=0.0)
    total_credits_disbursed: float = Field(ge=0.0)
    total_students: int = Field(ge=0)
    total_sessions: int = Field(ge=0)
    average_session_duration: float = Field(ge=0.0)
    top_institutions: List[Dict] = Field(default_factory=list)
    top_service_types: List[Dict] = Field(default_factory=list)
    
    # Export formats
    pdf_url: Optional[str] = None
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    def generate_report(self) -> None:
        """Generate report data"""
        pass
    
    def export_to_pdf(self) -> str:
        """Export report as PDF"""
        pass
    
    def export_to_csv(self) -> str:
        """Export report as CSV"""
        pass
    
    def send_to_stakeholders(self, email_list: List[str]) -> None:
        """Send report to stakeholder email list"""
        pass


class BlockchainRecord(BaseModel):
    """Model for blockchain transaction records"""
    
    record_id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: str = Field(regex=r'^(session|transaction|disbursement)$')
    entity_id: str = Field(min_length=1)
    blockchain_hash: str = Field(min_length=1)
    block_number: int = Field(ge=0)
    network: str = Field(default="ethereum")
    gas_used: Optional[int] = Field(None, ge=0)
    gas_price: Optional[float] = Field(None, ge=0.0)
    transaction_fee: Optional[float] = Field(None, ge=0.0)
    confirmations: int = Field(default=0, ge=0)
    is_confirmed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    def verify_on_chain(self) -> bool:
        """Verify record exists on blockchain"""
        pass
    
    def get_transaction_receipt(self) -> Dict:
        """Get blockchain transaction receipt"""
        pass