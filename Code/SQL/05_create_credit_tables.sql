-- CareCred Credit Management Tables - Normalized
-- Proper financial data modeling with audit trails

-- =====================================================
-- FINANCIAL INSTITUTIONS AND ACCOUNTS
-- =====================================================

-- Educational institutions for credit disbursement
CREATE TABLE educational_institutions (
    institution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_name VARCHAR(200) NOT NULL,
    institution_type VARCHAR(50), -- university, community_college, trade_school, etc.
    
    -- Contact information
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    
    -- Address
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_id INTEGER NOT NULL REFERENCES states(state_id),
    zip_code VARCHAR(10) NOT NULL,
    
    -- Banking information for disbursements
    bank_name VARCHAR(200),
    account_number_encrypted TEXT, -- Encrypted sensitive data
    routing_number_encrypted TEXT, -- Encrypted sensitive data
    account_type VARCHAR(20) CHECK (account_type IN ('checking', 'savings', 'institutional')),
    
    -- Integration details
    integration_type VARCHAR(20) CHECK (integration_type IN ('direct_api', 'file_transfer', 'manual')),
    api_endpoint TEXT,
    api_key_hash VARCHAR(255), -- Hashed API key
    file_transfer_protocol VARCHAR(20), -- sftp, ftp, s3, etc.
    
    -- Status and verification
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date DATE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    
    -- Financial tracking
    total_disbursements_lifetime DECIMAL(15, 2) DEFAULT 0.0 CHECK (total_disbursements_lifetime >= 0.0),
    pending_disbursements DECIMAL(15, 2) DEFAULT 0.0 CHECK (pending_disbursements >= 0.0),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Student credit accounts (one per student)
CREATE TABLE student_credit_accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student_profiles(user_id) ON DELETE CASCADE,
    
    -- Account identification
    account_number VARCHAR(20) UNIQUE NOT NULL, -- Human-readable account number
    
    -- Institution linkage
    primary_institution_id UUID REFERENCES educational_institutions(institution_id),
    
    -- Account balances (calculated from transactions)
    current_balance DECIMAL(12, 2) DEFAULT 0.0 CHECK (current_balance >= 0.0),
    pending_balance DECIMAL(12, 2) DEFAULT 0.0 CHECK (pending_balance >= 0.0),
    lifetime_earnings DECIMAL(12, 2) DEFAULT 0.0 CHECK (lifetime_earnings >= 0.0),
    lifetime_disbursements DECIMAL(12, 2) DEFAULT 0.0 CHECK (lifetime_disbursements >= 0.0),
    
    -- Account settings
    auto_disbursement_enabled BOOLEAN DEFAULT FALSE,
    auto_disbursement_threshold DECIMAL(10, 2) DEFAULT 100.00,
    min_disbursement_amount DECIMAL(10, 2) DEFAULT 25.00,
    
    -- Status
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'frozen', 'closed')),
    frozen_reason TEXT,
    frozen_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(student_id) -- One account per student
);

-- =====================================================
-- CREDIT TRANSACTIONS AND MOVEMENTS
-- =====================================================

-- All credit transactions (earnings, disbursements, adjustments)
CREATE TABLE credit_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES student_credit_accounts(account_id) ON DELETE CASCADE,
    
    -- Transaction identification
    transaction_number VARCHAR(30) UNIQUE NOT NULL, -- Human-readable transaction number
    transaction_type credit_transaction_type NOT NULL,
    
    -- Financial details
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0.0),
    currency VARCHAR(3) DEFAULT 'USD',
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Source/destination information
    source_type VARCHAR(50), -- session, adjustment, refund, government_payment
    source_id UUID, -- References various tables depending on source_type
    description TEXT NOT NULL CHECK (LENGTH(description) <= 500),
    
    -- Status tracking
    status credit_transaction_status DEFAULT 'pending',
    processing_started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    
    -- Authorization and approval
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES admin_profiles(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_notes TEXT,
    
    -- Audit trail
    created_by UUID REFERENCES users(user_id), -- Admin or system
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CREDIT DISBURSEMENTS
-- =====================================================

-- Disbursement requests and processing
CREATE TABLE credit_disbursements (
    disbursement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES student_credit_accounts(account_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_profiles(user_id),
    
    -- Disbursement identification
    disbursement_number VARCHAR(30) UNIQUE NOT NULL,
    
    -- Destination
    institution_id UUID REFERENCES educational_institutions(institution_id),
    institution_name VARCHAR(200) NOT NULL, -- Stored for audit trail
    disbursement_category disbursement_category NOT NULL,
    
    -- Financial details
    requested_amount DECIMAL(10, 2) NOT NULL CHECK (requested_amount > 0.0),
    approved_amount DECIMAL(10, 2) CHECK (approved_amount >= 0.0),
    actual_amount DECIMAL(10, 2) CHECK (actual_amount >= 0.0),
    
    -- Processing fees
    processing_fee DECIMAL(8, 2) DEFAULT 0.0 CHECK (processing_fee >= 0.0),
    institution_fee DECIMAL(8, 2) DEFAULT 0.0 CHECK (institution_fee >= 0.0),
    net_amount DECIMAL(10, 2) CHECK (net_amount >= 0.0),
    
    -- Payment details
    payment_method payment_method DEFAULT 'ach',
    payment_reference VARCHAR(100), -- External payment system reference
    
    -- Status and timing
    status credit_transaction_status DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Authorization
    requested_by UUID NOT NULL REFERENCES users(user_id), -- Usually the student
    approved_by UUID REFERENCES admin_profiles(user_id),
    processed_by UUID REFERENCES admin_profiles(user_id),
    
    -- Related transactions
    credit_transaction_id UUID REFERENCES credit_transactions(transaction_id),
    
    -- Error handling and retries
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    
    -- Special handling
    is_emergency_disbursement BOOLEAN DEFAULT FALSE,
    emergency_reason TEXT,
    requires_verification BOOLEAN DEFAULT TRUE,
    verification_completed BOOLEAN DEFAULT FALSE,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Disbursement allocation breakdown (for mixed disbursements)
CREATE TABLE disbursement_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disbursement_id UUID NOT NULL REFERENCES credit_disbursements(disbursement_id) ON DELETE CASCADE,
    
    category disbursement_category NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0.0),
    percentage DECIMAL(5, 2) NOT NULL CHECK (percentage > 0.0 AND percentage <= 100.0),
    
    -- Institution-specific details
    institution_account_reference VARCHAR(100),
    institution_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- GOVERNMENT FUNDING AND PAYMENTS
-- =====================================================

-- Government payments received by the platform
CREATE TABLE government_payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    funding_source_id UUID NOT NULL REFERENCES funding_sources(funding_source_id),
    
    -- Payment identification
    payment_reference VARCHAR(100) NOT NULL UNIQUE, -- Government reference number
    payment_description TEXT NOT NULL,
    
    -- Financial details
    total_amount DECIMAL(15, 2) NOT NULL CHECK (total_amount > 0.0),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Timing
    payment_date DATE NOT NULL,
    received_date DATE,
    reporting_period_start DATE NOT NULL,
    reporting_period_end DATE NOT NULL,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'expected' CHECK (status IN ('expected', 'received', 'allocated', 'reconciled')),
    
    -- Allocation tracking
    total_allocated DECIMAL(15, 2) DEFAULT 0.0 CHECK (total_allocated >= 0.0),
    remaining_balance DECIMAL(15, 2),
    allocation_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing
    processed_by UUID REFERENCES admin_profiles(user_id),
    reconciled_by UUID REFERENCES admin_profiles(user_id),
    reconciled_at TIMESTAMP WITH TIME ZONE,
    
    -- Documents and audit
    payment_document_url TEXT,
    bank_reference VARCHAR(100),
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_payment_period CHECK (reporting_period_end > reporting_period_start)
);

-- Payment allocations to individual students
CREATE TABLE payment_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES government_payments(payment_id),
    student_id UUID NOT NULL REFERENCES student_profiles(user_id),
    account_id UUID NOT NULL REFERENCES student_credit_accounts(account_id),
    
    -- Service period covered by this allocation
    service_period_start DATE NOT NULL,
    service_period_end DATE NOT NULL,
    
    -- Hours and rates
    verified_hours DECIMAL(8, 2) NOT NULL CHECK (verified_hours >= 0.0),
    hourly_rate DECIMAL(6, 2) NOT NULL CHECK (hourly_rate > 0.0),
    gross_amount DECIMAL(10, 2) NOT NULL CHECK (gross_amount >= 0.0),
    
    -- Deductions
    platform_fee_percentage DECIMAL(5, 2) DEFAULT 5.0,
    platform_fee_amount DECIMAL(10, 2) DEFAULT 0.0 CHECK (platform_fee_amount >= 0.0),
    tax_withholding_amount DECIMAL(10, 2) DEFAULT 0.0 CHECK (tax_withholding_amount >= 0.0),
    other_deductions DECIMAL(10, 2) DEFAULT 0.0 CHECK (other_deductions >= 0.0),
    
    -- Net payment
    net_amount DECIMAL(10, 2) NOT NULL CHECK (net_amount >= 0.0),
    
    -- Session references (JSON array of session IDs)
    session_ids JSONB DEFAULT '[]'::jsonb,
    
    -- Processing
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_by UUID NOT NULL REFERENCES admin_profiles(user_id),
    
    -- Verification
    hours_verified_by UUID REFERENCES admin_profiles(user_id),
    hours_verified_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_service_period CHECK (service_period_end > service_period_start)
);

-- =====================================================
-- FINANCIAL REPORTING AND ANALYTICS
-- =====================================================

-- Financial reports for compliance and analytics
CREATE TABLE financial_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Report identification
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN (
        'monthly_summary', 'quarterly_summary', 'annual_summary', 
        'student_earnings', 'institution_disbursements', 'government_reconciliation',
        'tax_reporting', 'audit_trail'
    )),
    report_name VARCHAR(200) NOT NULL,
    
    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Report data
    report_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Summary statistics
    total_credits_issued DECIMAL(15, 2) DEFAULT 0.0,
    total_credits_disbursed DECIMAL(15, 2) DEFAULT 0.0,
    total_students_active INTEGER DEFAULT 0,
    total_sessions_completed INTEGER DEFAULT 0,
    average_hourly_rate DECIMAL(6, 2) DEFAULT 0.0,
    
    -- Generation details
    generated_by UUID NOT NULL REFERENCES admin_profiles(user_id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Export formats
    pdf_url TEXT,
    csv_url TEXT,
    excel_url TEXT,
    
    -- Status
    is_finalized BOOLEAN DEFAULT FALSE,
    finalized_by UUID REFERENCES admin_profiles(user_id),
    finalized_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_period_range CHECK (period_end > period_start)
);

-- =====================================================
-- BLOCKCHAIN INTEGRATION FOR CREDITS
-- =====================================================

-- Blockchain records for credit transactions
CREATE TABLE credit_blockchain_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Entity reference
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('transaction', 'disbursement', 'session', 'allocation')),
    entity_id UUID NOT NULL,
    
    -- Blockchain details
    blockchain_network VARCHAR(20) DEFAULT 'solana',
    transaction_hash VARCHAR(255) NOT NULL,
    block_number INTEGER NOT NULL CHECK (block_number >= 0),
    block_hash VARCHAR(255),
    
    -- Transaction costs
    gas_used INTEGER CHECK (gas_used >= 0),
    gas_price DECIMAL(12, 8) CHECK (gas_price >= 0.0),
    transaction_fee DECIMAL(12, 8) CHECK (transaction_fee >= 0.0),
    
    -- Confirmation status
    confirmations INTEGER DEFAULT 0 CHECK (confirmations >= 0),
    is_confirmed BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    
    -- Data integrity
    data_hash VARCHAR(255) NOT NULL, -- Hash of the data stored on blockchain
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'failed')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(transaction_hash)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Educational institutions indexes
CREATE INDEX idx_educational_institutions_state ON educational_institutions(state_id);
CREATE INDEX idx_educational_institutions_verified ON educational_institutions(is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_educational_institutions_active ON educational_institutions(is_active) WHERE is_active = TRUE;

-- Credit accounts indexes
CREATE INDEX idx_student_credit_accounts_student ON student_credit_accounts(student_id);
CREATE INDEX idx_student_credit_accounts_institution ON student_credit_accounts(primary_institution_id);
CREATE INDEX idx_student_credit_accounts_status ON student_credit_accounts(account_status);
CREATE INDEX idx_student_credit_accounts_active ON student_credit_accounts(account_status) WHERE account_status = 'active';

-- Transactions indexes
CREATE INDEX idx_credit_transactions_account ON credit_transactions(account_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(transaction_type);
CREATE INDEX idx_credit_transactions_status ON credit_transactions(status);
CREATE INDEX idx_credit_transactions_effective_date ON credit_transactions(effective_date);
CREATE INDEX idx_credit_transactions_source ON credit_transactions(source_type, source_id);
CREATE INDEX idx_credit_transactions_pending ON credit_transactions(status) WHERE status = 'pending';

-- Disbursements indexes
CREATE INDEX idx_credit_disbursements_account ON credit_disbursements(account_id);
CREATE INDEX idx_credit_disbursements_student ON credit_disbursements(student_id);
CREATE INDEX idx_credit_disbursements_institution ON credit_disbursements(institution_id);
CREATE INDEX idx_credit_disbursements_status ON credit_disbursements(status);
CREATE INDEX idx_credit_disbursements_requested_at ON credit_disbursements(requested_at);
CREATE INDEX idx_credit_disbursements_pending ON credit_disbursements(status) WHERE status IN ('pending', 'processing');

-- Government payments indexes
CREATE INDEX idx_government_payments_funding_source ON government_payments(funding_source_id);
CREATE INDEX idx_government_payments_period ON government_payments(reporting_period_start, reporting_period_end);
CREATE INDEX idx_government_payments_status ON government_payments(status);
CREATE INDEX idx_government_payments_received_date ON government_payments(received_date);

-- Payment allocations indexes
CREATE INDEX idx_payment_allocations_payment ON payment_allocations(payment_id);
CREATE INDEX idx_payment_allocations_student ON payment_allocations(student_id);
CREATE INDEX idx_payment_allocations_period ON payment_allocations(service_period_start, service_period_end);

-- Blockchain records indexes
CREATE INDEX idx_credit_blockchain_records_entity ON credit_blockchain_records(entity_type, entity_id);
CREATE INDEX idx_credit_blockchain_records_hash ON credit_blockchain_records(transaction_hash);
CREATE INDEX idx_credit_blockchain_records_confirmed ON credit_blockchain_records(is_confirmed) WHERE is_confirmed = TRUE;

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Auto-generate account numbers
CREATE OR REPLACE FUNCTION generate_account_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.account_number := 'CCA-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' || 
                         LPAD(NEXTVAL('account_number_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for account numbers
CREATE SEQUENCE account_number_seq START 100001;

-- Trigger for account number generation
CREATE TRIGGER generate_account_number_trigger
    BEFORE INSERT ON student_credit_accounts
    FOR EACH ROW
    EXECUTE FUNCTION generate_account_number();

-- Auto-generate transaction numbers
CREATE OR REPLACE FUNCTION generate_transaction_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.transaction_number := 'TXN-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                             LPAD(NEXTVAL('transaction_number_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for transaction numbers
CREATE SEQUENCE transaction_number_seq START 1;

-- Trigger for transaction number generation
CREATE TRIGGER generate_transaction_number_trigger
    BEFORE INSERT ON credit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION generate_transaction_number();

-- Auto-generate disbursement numbers
CREATE OR REPLACE FUNCTION generate_disbursement_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.disbursement_number := 'DIS-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                              LPAD(NEXTVAL('disbursement_number_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for disbursement numbers
CREATE SEQUENCE disbursement_number_seq START 1;

-- Trigger for disbursement number generation
CREATE TRIGGER generate_disbursement_number_trigger
    BEFORE INSERT ON credit_disbursements
    FOR EACH ROW
    EXECUTE FUNCTION generate_disbursement_number();

-- Function to update account balances when transactions change
CREATE OR REPLACE FUNCTION update_account_balances()
RETURNS TRIGGER AS $$
DECLARE
    account_record student_credit_accounts%ROWTYPE;
    total_earned DECIMAL(12, 2) := 0.0;
    total_disbursed DECIMAL(12, 2) := 0.0;
    total_pending DECIMAL(12, 2) := 0.0;
BEGIN
    -- Get account info
    SELECT * INTO account_record 
    FROM student_credit_accounts 
    WHERE account_id = COALESCE(NEW.account_id, OLD.account_id);
    
    IF NOT FOUND THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    
    -- Calculate totals from all transactions
    SELECT 
        COALESCE(SUM(CASE WHEN transaction_type = 'earned' AND status = 'completed' THEN amount ELSE 0 END), 0.0),
        COALESCE(SUM(CASE WHEN transaction_type = 'disbursed' AND status = 'completed' THEN amount ELSE 0 END), 0.0),
        COALESCE(SUM(CASE WHEN status IN ('pending', 'processing') THEN amount ELSE 0 END), 0.0)
    INTO total_earned, total_disbursed, total_pending
    FROM credit_transactions 
    WHERE account_id = account_record.account_id;
    
    -- Update account balances
    UPDATE student_credit_accounts 
    SET 
        lifetime_earnings = total_earned,
        lifetime_disbursements = total_disbursed,
        pending_balance = total_pending,
        current_balance = GREATEST(0.0, total_earned - total_disbursed),
        updated_at = CURRENT_TIMESTAMP
    WHERE account_id = account_record.account_id;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to update balances when transactions change
CREATE TRIGGER update_account_balances_trigger
    AFTER INSERT OR UPDATE OR DELETE ON credit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_account_balances();

-- Function to validate disbursement allocation percentages
CREATE OR REPLACE FUNCTION validate_disbursement_allocations()
RETURNS TRIGGER AS $$
DECLARE
    total_percentage DECIMAL(5, 2) := 0.0;
BEGIN
    -- Calculate total percentage for this disbursement
    SELECT COALESCE(SUM(percentage), 0.0) INTO total_percentage
    FROM disbursement_allocations
    WHERE disbursement_id = NEW.disbursement_id
    AND allocation_id != NEW.allocation_id; -- Exclude current record for updates
    
    total_percentage := total_percentage + NEW.percentage;
    
    -- Validate total doesn't exceed 100%
    IF total_percentage > 100.0 THEN
        RAISE EXCEPTION 'Total allocation percentage cannot exceed 100%%. Current total would be: %', total_percentage;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for allocation validation
CREATE TRIGGER validate_disbursement_allocations_trigger
    BEFORE INSERT OR UPDATE ON disbursement_allocations
    FOR EACH ROW
    EXECUTE FUNCTION validate_disbursement_allocations();

-- Add updated_at triggers
CREATE TRIGGER update_educational_institutions_updated_at BEFORE UPDATE ON educational_institutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_credit_accounts_updated_at BEFORE UPDATE ON student_credit_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credit_transactions_updated_at BEFORE UPDATE ON credit_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credit_disbursements_updated_at BEFORE UPDATE ON credit_disbursements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_government_payments_updated_at BEFORE UPDATE ON government_payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();