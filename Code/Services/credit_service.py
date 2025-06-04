from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Union
from pydantic import BaseModel
from ..Models.credit import (
    CreditAccount, CreditTransaction, CreditDisbursement, 
    InstitutionAccount, CreditReport, CreditTransactionType,
    CreditTransactionStatus, DisbursementType, PaymentMethod,
    BlockchainRecord
)
from ..Models.session import Session


class CreditCalculationResult(BaseModel):
    """Result object for credit calculations"""
    
    total_amount: float = 0.0
    base_amount: float = 0.0
    bonuses: Dict[str, float] = {}
    deductions: Dict[str, float] = {}
    breakdown: Dict[str, float] = {}
    calculation_notes: Optional[str] = None


class DisbursementResult(BaseModel):
    """Result object for credit disbursement operations"""
    
    success: bool = False
    disbursement_id: Optional[str] = None
    amount_disbursed: float = 0.0
    institution_confirmation: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None  # seconds


class CreditAnalytics(BaseModel):
    """Result object for credit analytics"""
    
    total_credits_issued: float
    total_credits_disbursed: float
    pending_disbursements: float
    active_student_accounts: int
    average_session_credit: float
    top_earning_students: List[Dict[str, Union[str, float]]]
    disbursement_trends: Dict[str, List[float]]
    
    class Config:
        arbitrary_types_allowed = True


class CreditService:
    """Service for managing student credits and disbursements"""
    
    def __init__(self, database_connection, blockchain_service, notification_service):
        self.base_hourly_rate: float = 15.00
        self.bonus_multipliers: Dict[str, float] = {
            "first_time_senior": 1.1,
            "high_rated_session": 1.05,
            "emergency_help": 1.2,
            "weekend_service": 1.1,
            "holiday_service": 1.15,
            "perfect_attendance": 1.05
        }
        self.minimum_disbursement_amount: float = 50.0
        self.maximum_pending_credits: float = 1000.0
        self.processing_fee_percentage: float = 2.5
    
    def create_credit_account(self, student_id: str, institution_info: Dict[str, str]) -> CreditAccount:
        """
        Create new credit account for student
        
        Args:
            student_id: ID of student
            institution_info: Dictionary with institution details
                Required fields: institution_name, account_number (optional),
                routing_number (optional)
        
        Returns:
            Created CreditAccount object
        """
        pass
    
    def calculate_session_credits(self, session: Session, bonus_factors: List[str] = None) -> CreditCalculationResult:
        """
        Calculate credits earned for a completed session
        
        Args:
            session: Completed session object
            bonus_factors: Optional list of bonus factors to apply
        
        Returns:
            CreditCalculationResult with detailed breakdown
        """
        pass
    
    def award_credits(self, session_id: str, student_id: str, amount: float, calculation_breakdown: Dict[str, float] = None) -> CreditTransaction:
        """
        Award credits to student for completed session
        
        Args:
            session_id: ID of completed session
            student_id: ID of student to award credits
            amount: Credit amount to award
            calculation_breakdown: Optional breakdown of calculation
        
        Returns:
            Created CreditTransaction object
        """
        pass
    
    def get_account_balance(self, student_id: str, include_pending: bool = True) -> Dict[str, Union[float, int, datetime]]:
        """
        Get current credit account balance and details
        
        Args:
            student_id: ID of student
            include_pending: Whether to include pending credits
        
        Returns:
            Dictionary with balance details, transaction counts, and timestamps
        """
        pass
    
    def get_transaction_history(self, student_id: str, limit: int = 50, offset: int = 0, transaction_type: CreditTransactionType = None) -> List[CreditTransaction]:
        """
        Get credit transaction history for student
        
        Args:
            student_id: ID of student
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip (for pagination)
            transaction_type: Optional filter by transaction type
        
        Returns:
            List of CreditTransaction objects
        """
        pass
    
    def request_disbursement(self, student_id: str, amount: float, disbursement_type: DisbursementType, allocation_preferences: Dict[str, float] = None) -> str:
        """
        Request credit disbursement to institution
        
        Args:
            student_id: ID of student requesting disbursement
            amount: Amount to disburse
            disbursement_type: Type of disbursement
            allocation_preferences: Optional custom allocation percentages
        
        Returns:
            Disbursement request ID for tracking
        """
        pass
    
    def approve_disbursement(self, disbursement_id: str, admin_id: str, notes: str = None) -> DisbursementResult:
        """
        Approve pending credit disbursement
        
        Args:
            disbursement_id: ID of disbursement to approve
            admin_id: ID of admin approving
            notes: Optional approval notes
        
        Returns:
            DisbursementResult with approval details
        """
        pass
    
    def reject_disbursement(self, disbursement_id: str, admin_id: str, reason: str) -> bool:
        """
        Reject pending credit disbursement
        
        Args:
            disbursement_id: ID of disbursement to reject
            admin_id: ID of admin rejecting
            reason: Reason for rejection
        
        Returns:
            True if rejection recorded successfully
        """
        pass
    
    def process_disbursement(self, disbursement_id: str, admin_id: str, payment_method: PaymentMethod = PaymentMethod.ACH) -> DisbursementResult:
        """
        Process approved disbursement to institution
        
        Args:
            disbursement_id: ID of approved disbursement
            admin_id: ID of admin processing
            payment_method: Method of payment to institution
        
        Returns:
            DisbursementResult with processing details
        """
        pass
    
    def get_pending_disbursements(self, institution_id: str = None, admin_view: bool = False) -> List[CreditDisbursement]:
        """
        Get all pending disbursements, optionally filtered by institution
        
        Args:
            institution_id: Optional filter by institution
            admin_view: Whether requesting admin has access to all fields
        
        Returns:
            List of pending CreditDisbursement objects
        """
        pass
    
    def update_disbursement_preferences(self, student_id: str, preferences: Dict[str, float]) -> bool:
        """
        Update student's disbursement allocation preferences
        
        Args:
            student_id: ID of student
            preferences: Dictionary mapping disbursement types to percentages
        
        Returns:
            True if update successful
        """
        pass
    
    def calculate_disbursement_split(self, total_amount: float, preferences: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate disbursement amounts based on allocation preferences
        
        Args:
            total_amount: Total amount to disburse
            preferences: Allocation percentages by category
        
        Returns:
            Dictionary mapping categories to dollar amounts
        """
        pass
    
    def reverse_transaction(self, transaction_id: str, admin_id: str, reason: str) -> CreditTransaction:
        """
        Reverse a credit transaction (refund/adjustment)
        
        Args:
            transaction_id: ID of transaction to reverse
            admin_id: ID of admin performing reversal
            reason: Reason for reversal
        
        Returns:
            New CreditTransaction object for the reversal
        """
        pass
    
    def apply_credit_adjustment(self, student_id: str, amount: float, admin_id: str, reason: str, adjustment_type: str = "manual") -> CreditTransaction:
        """
        Apply manual credit adjustment (positive or negative)
        
        Args:
            student_id: ID of student
            amount: Adjustment amount (positive or negative)
            admin_id: ID of admin making adjustment
            reason: Reason for adjustment
            adjustment_type: Type of adjustment (manual, system_correction, etc.)
        
        Returns:
            Created CreditTransaction object
        """
        pass
    
    def get_credit_analytics(self, start_date: datetime, end_date: datetime, institution_id: str = None) -> CreditAnalytics:
        """
        Get credit system analytics for date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            institution_id: Optional filter by institution
        
        Returns:
            CreditAnalytics object with comprehensive metrics
        """
        pass
    
    def bulk_process_disbursements(self, disbursement_ids: List[str], admin_id: str) -> Dict[str, DisbursementResult]:
        """
        Bulk process multiple disbursements
        
        Args:
            disbursement_ids: List of disbursement IDs to process
            admin_id: ID of admin processing
        
        Returns:
            Dictionary mapping disbursement_id to DisbursementResult
        """
        pass
    
    def freeze_account(self, student_id: str, admin_id: str, reason: str) -> bool:
        """
        Freeze student credit account (prevent new transactions)
        
        Args:
            student_id: ID of student account to freeze
            admin_id: ID of admin freezing account
            reason: Reason for freeze
        
        Returns:
            True if account frozen successfully
        """
        pass
    
    def unfreeze_account(self, student_id: str, admin_id: str) -> bool:
        """
        Unfreeze student credit account
        
        Args:
            student_id: ID of student account to unfreeze
            admin_id: ID of admin unfreezing account
        
        Returns:
            True if account unfrozen successfully
        """
        pass


class InstitutionIntegrationService:
    """Service for integrating with educational institutions"""
    
    def __init__(self, database_connection, encryption_service):
        self.supported_integrations: List[str] = ["direct_api", "sftp", "manual", "webhook"]
        self.connection_timeout_seconds: int = 30
        self.retry_attempts: int = 3
        self.batch_size: int = 100
        self.max_daily_disbursements: int = 1000
    
    def register_institution(self, institution_data: Dict[str, Union[str, bool]]) -> InstitutionAccount:
        """
        Register new educational institution
        
        Args:
            institution_data: Dictionary with institution details
                Required fields: institution_name, contact_name, contact_email,
                contact_phone, integration_type
                Optional fields: api_endpoint, account_number, routing_number
        
        Returns:
            Created InstitutionAccount object
        """
        pass
    
    def test_institution_connection(self, institution_id: str) -> Dict[str, Union[bool, str, float]]:
        """
        Test connection to institution's systems
        
        Args:
            institution_id: ID of institution to test
        
        Returns:
            Dictionary with connection status, response time, and error details
        """
        pass
    
    def sync_student_enrollment(self, institution_id: str, force_refresh: bool = False) -> Dict[str, Union[int, List[str]]]:
        """
        Sync student enrollment data with institution
        
        Args:
            institution_id: ID of institution
            force_refresh: Whether to force complete refresh of data
        
        Returns:
            Dictionary with sync results, counts, and any errors
        """
        pass
    
    def submit_disbursement_batch(self, institution_id: str, disbursements: List[CreditDisbursement]) -> Dict[str, Union[str, int, List[str]]]:
        """
        Submit batch of disbursements to institution
        
        Args:
            institution_id: ID of target institution
            disbursements: List of disbursements to submit
        
        Returns:
            Dictionary with batch ID, submission count, and any failures
        """
        pass
    
    def check_disbursement_status(self, institution_id: str, disbursement_ids: List[str]) -> Dict[str, Dict[str, Union[str, datetime]]]:
        """
        Check status of submitted disbursements
        
        Args:
            institution_id: ID of institution
            disbursement_ids: List of disbursement IDs to check
        
        Returns:
            Dictionary mapping disbursement_id to status information
        """
        pass
    
    def get_student_account_info(self, institution_id: str, student_id: str) -> Dict[str, Union[str, float, bool]]:
        """
        Get student account information from institution
        
        Args:
            institution_id: ID of institution
            student_id: ID of student
        
        Returns:
            Dictionary with student account details and balances
        """
        pass
    
    def update_institution_settings(self, institution_id: str, settings: Dict[str, Union[str, int, bool]], admin_id: str) -> bool:
        """
        Update institution integration settings
        
        Args:
            institution_id: ID of institution
            settings: Dictionary with new settings
            admin_id: ID of admin making changes
        
        Returns:
            True if update successful
        """
        pass
    
    def generate_disbursement_report(self, institution_id: str, start_date: datetime, end_date: datetime) -> CreditReport:
        """
        Generate disbursement report for institution
        
        Args:
            institution_id: ID of institution
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            CreditReport object with institution-specific data
        """
        pass
    
    def handle_institution_webhook(self, institution_id: str, webhook_data: Dict, signature: str = None) -> None:
        """
        Handle webhook notifications from institution
        
        Args:
            institution_id: ID of institution sending webhook
            webhook_data: Webhook payload data
            signature: Optional webhook signature for verification
        """
        pass
    
    def validate_institution_credentials(self, institution_id: str) -> Tuple[bool, str]:
        """
        Validate institution API credentials
        
        Args:
            institution_id: ID of institution to validate
        
        Returns:
            Tuple of (is_valid, error_message_if_invalid)
        """
        pass


class BlockchainIntegrationService:
    """Service for blockchain integration and verification"""
    
    def __init__(self, blockchain_config: Dict[str, Union[str, int]]):
        self.blockchain_network: str = blockchain_config.get("network", "ethereum")
        self.contract_address: str = blockchain_config.get("contract_address")
        self.gas_limit: int = blockchain_config.get("gas_limit", 100000)
        self.confirmation_blocks: int = blockchain_config.get("confirmations", 3)
        self.max_gas_price: float = blockchain_config.get("max_gas_price", 50.0)  # gwei
    
    def record_session_on_blockchain(self, session_id: str, session_data: Dict[str, Union[str, float, datetime]]) -> str:
        """
        Record session completion on blockchain
        
        Args:
            session_id: ID of completed session
            session_data: Session data to record (duration, credits, participants)
        
        Returns:
            Blockchain transaction hash
        """
        pass
    
    def record_credit_transaction(self, transaction_id: str, transaction_data: Dict[str, Union[str, float]]) -> str:
        """
        Record credit transaction on blockchain
        
        Args:
            transaction_id: ID of credit transaction
            transaction_data: Transaction data (amount, type, participants)
        
        Returns:
            Blockchain transaction hash
        """
        pass
    
    def verify_blockchain_record(self, transaction_hash: str) -> Dict[str, Union[bool, int, datetime]]:
        """
        Verify blockchain transaction exists and is confirmed
        
        Args:
            transaction_hash: Blockchain transaction hash
        
        Returns:
            Dictionary with verification status, confirmations, and timestamp
        """
        pass
    
    def get_transaction_receipt(self, transaction_hash: str) -> Dict[str, Union[str, int, float]]:
        """
        Get blockchain transaction receipt
        
        Args:
            transaction_hash: Blockchain transaction hash
        
        Returns:
            Dictionary with transaction receipt details
        """
        pass
    
    def estimate_gas_cost(self, operation_type: str, data_size: int = 1) -> float:
        """
        Estimate gas cost for blockchain operation
        
        Args:
            operation_type: Type of operation (session_record, credit_transaction)
            data_size: Size of data to record (in KB)
        
        Returns:
            Estimated gas cost in USD
        """
        pass
    
    def check_blockchain_sync_status(self) -> Dict[str, Union[bool, int, datetime]]:
        """
        Check if blockchain integration is in sync
        
        Returns:
            Dictionary with sync status, block height, and last sync time
        """
        pass
    
    def generate_proof_of_service(self, session_id: str) -> Dict[str, str]:
        """
        Generate cryptographic proof of service completion
        
        Args:
            session_id: ID of completed session
        
        Returns:
            Dictionary with proof data and verification instructions
        """
        pass
    
    def validate_proof_of_service(self, proof_data: Dict[str, str]) -> bool:
        """
        Validate cryptographic proof of service
        
        Args:
            proof_data: Proof data to validate
        
        Returns:
            True if proof is valid, False otherwise
        """
        pass
    
    def get_blockchain_analytics(self) -> Dict[str, Union[int, float, List]]:
        """
        Get blockchain integration analytics
        
        Returns:
            Dictionary with transaction counts, costs, and performance metrics
        """
        pass
    
    def batch_record_transactions(self, transactions: List[Dict]) -> List[str]:
        """
        Batch record multiple transactions on blockchain
        
        Args:
            transactions: List of transaction data to record
        
        Returns:
            List of blockchain transaction hashes
        """
        pass


class ReportingService:
    """Service for generating credit and financial reports"""
    
    def __init__(self, database_connection, file_storage_service):
        self.report_retention_days: int = 2555  # 7 years for compliance
        self.export_formats: List[str] = ["pdf", "csv", "excel", "json"]
        self.scheduled_reports: Dict[str, Dict] = {}
        self.max_report_size_mb: int = 100
    
    def generate_monthly_report(self, year: int, month: int, institution_id: str = None) -> CreditReport:
        """
        Generate monthly credit system report
        
        Args:
            year: Report year
            month: Report month (1-12)
            institution_id: Optional filter by institution
        
        Returns:
            Generated CreditReport object
        """
        pass
    
    def generate_quarterly_report(self, year: int, quarter: int) -> CreditReport:
        """
        Generate quarterly financial report
        
        Args:
            year: Report year
            quarter: Report quarter (1-4)
        
        Returns:
            Generated CreditReport object
        """
        pass
    
    def generate_annual_report(self, year: int) -> CreditReport:
        """
        Generate annual compliance report
        
        Args:
            year: Report year
        
        Returns:
            Generated CreditReport object
        """
        pass
    
    def generate_institution_report(self, institution_id: str, start_date: datetime, end_date: datetime) -> CreditReport:
        """
        Generate report for specific institution
        
        Args:
            institution_id: ID of institution
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Generated CreditReport object
        """
        pass
    
    def generate_student_statement(self, student_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Union[str, float, List]]:
        """
        Generate credit statement for student
        
        Args:
            student_id: ID of student
            start_date: Statement start date
            end_date: Statement end date
        
        Returns:
            Dictionary with statement data and summary
        """
        pass
    
    def export_report(self, report_id: str, format: str) -> str:
        """
        Export report in specified format
        
        Args:
            report_id: ID of report to export
            format: Export format (pdf, csv, excel, json)
        
        Returns:
            URL or file path of exported report
        """
        pass
    
    def schedule_automated_report(self, report_type: str, frequency: str, recipients: List[str], filters: Dict = None) -> str:
        """
        Schedule automated report generation
        
        Args:
            report_type: Type of report to generate
            frequency: How often to generate (daily, weekly, monthly)
            recipients: List of email addresses to send to
            filters: Optional filters to apply
        
        Returns:
            Scheduled report ID
        """
        pass
    
    def get_compliance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Union[float, int, bool]]:
        """
        Get compliance metrics for regulatory reporting
        
        Args:
            start_date: Metrics start date
            end_date: Metrics end date
        
        Returns:
            Dictionary with compliance metrics and flags
        """
        pass
    
    def audit_trail_report(self, start_date: datetime, end_date: datetime, entity_type: str = None) -> Dict[str, Union[int, List]]:
        """
        Generate audit trail report for all credit transactions
        
        Args:
            start_date: Audit period start
            end_date: Audit period end
            entity_type: Optional filter by entity type
        
        Returns:
            Dictionary with audit trail data and summary
        """
        pass
    
    def tax_reporting_export(self, tax_year: int, student_ids: List[str] = None) -> str:
        """
        Export tax reporting data for students (1099 forms)
        
        Args:
            tax_year: Tax year for reporting
            student_ids: Optional list of specific students
        
        Returns:
            File path of tax reporting export
        """
        pass
    
    def real_time_dashboard_data(self) -> Dict[str, Union[float, int, List]]:
        """
        Get real-time data for financial dashboard
        
        Returns:
            Dictionary with current metrics and trends
        """
        pass