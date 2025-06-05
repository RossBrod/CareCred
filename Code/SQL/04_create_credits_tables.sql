-- CareCred Credits and Financial Tables

-- Student credit accounts
CREATE TABLE credit_accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_credits_earned DECIMAL(12, 2) DEFAULT 0.0 CHECK (total_credits_earned >= 0.0),
    total_credits_disbursed DECIMAL(12, 2) DEFAULT 0.0 CHECK (total_credits_disbursed >= 0.0),
    pending_credits DECIMAL(12, 2) DEFAULT 0.0 CHECK (pending_credits >= 0.0),
    available_balance DECIMAL(12, 2) DEFAULT 0.0 CHECK (available_balance >= 0.0),
    lifetime_earnings DECIMAL(12, 2) DEFAULT 0.0 CHECK (lifetime_earnings >= 0.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Institution account details
    institution_name VARCHAR(200),
    institution_account_number VARCHAR(50),
    institution_routing_number VARCHAR(20),
    
    -- Disbursement preferences (JSON for flexibility)
    default_disbursement_split JSONB DEFAULT '{"tuition": 60.0, "housing": 40.0}'::jsonb,
    
    UNIQUE(student_id)
);

-- Individual credit transactions
CREATE TABLE credit_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES credit_accounts(account_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(user_id),
    session_id UUID REFERENCES sessions(session_id),
    transaction_type credit_transaction_type NOT NULL,
    status credit_transaction_status DEFAULT 'pending',
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0.0),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES users(user_id), -- admin_id
    
    -- Blockchain verification
    blockchain_hash VARCHAR(255),
    blockchain_verified BOOLEAN DEFAULT FALSE,
    blockchain_block_number INTEGER,
    blockchain_confirmations INTEGER DEFAULT 0,
    credit_eligibility_verified BOOLEAN DEFAULT FALSE,
    
    -- Disbursement specific fields
    disbursement_type disbursement_type,
    institution_reference VARCHAR(100),
    disbursement_batch_id UUID
);

-- Institution accounts for integration
CREATE TABLE institution_accounts (
    institution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    account_number VARCHAR(50),
    routing_number VARCHAR(20),
    api_endpoint TEXT,
    api_key_hash VARCHAR(255), -- encrypted
    integration_type VARCHAR(20) CHECK (integration_type IN ('direct_api', 'file_transfer', 'manual')),
    is_active BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP WITH TIME ZONE,
    total_disbursements DECIMAL(15, 2) DEFAULT 0.0 CHECK (total_disbursements >= 0.0),
    pending_disbursements DECIMAL(15, 2) DEFAULT 0.0 CHECK (pending_disbursements >= 0.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Credit disbursements to institutions
CREATE TABLE credit_disbursements (
    disbursement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(user_id),
    account_id UUID NOT NULL REFERENCES credit_accounts(account_id),
    institution_id UUID REFERENCES institution_accounts(institution_id),
    institution_name VARCHAR(200) NOT NULL,
    disbursement_type disbursement_type NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0.0),
    status credit_transaction_status DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(user_id), -- admin_id
    processed_by UUID REFERENCES users(user_id), -- admin_id
    
    -- Institution integration
    institution_transaction_id VARCHAR(100),
    institution_confirmation VARCHAR(200),
    payment_method payment_method DEFAULT 'ach',
    
    -- Related transactions and sessions
    transaction_ids JSONB DEFAULT '[]'::jsonb,
    session_ids JSONB DEFAULT '[]'::jsonb,
    
    -- Error handling
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE
);

-- Credit reports for analytics and compliance
CREATE TABLE credit_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(20) CHECK (report_type IN ('monthly', 'quarterly', 'annual', 'custom')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_by UUID NOT NULL REFERENCES users(user_id), -- admin_id
    
    -- Report data
    total_credits_issued DECIMAL(15, 2) DEFAULT 0.0,
    total_credits_disbursed DECIMAL(15, 2) DEFAULT 0.0,
    total_students INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    average_session_duration DECIMAL(6, 2) DEFAULT 0.0,
    top_institutions JSONB DEFAULT '[]'::jsonb,
    top_service_types JSONB DEFAULT '[]'::jsonb,
    
    -- Export formats
    pdf_url TEXT,
    csv_url TEXT,
    excel_url TEXT,
    
    CONSTRAINT check_date_range CHECK (end_date > start_date)
);

-- Government payment tracking
CREATE TABLE government_payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_source VARCHAR(200) NOT NULL, -- e.g., "Federal Grant - April 2025"
    total_amount DECIMAL(15, 2) NOT NULL CHECK (total_amount > 0.0),
    payment_date DATE NOT NULL,
    received_date DATE,
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    report_reference VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'received', 'allocated', 'disbursed')),
    
    -- Allocation tracking
    total_allocated DECIMAL(15, 2) DEFAULT 0.0,
    remaining_balance DECIMAL(15, 2),
    allocation_completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_payment_period CHECK (report_period_end > report_period_start)
);

-- Government payment allocations to students
CREATE TABLE payment_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES government_payments(payment_id),
    student_id UUID NOT NULL REFERENCES users(user_id),
    account_id UUID NOT NULL REFERENCES credit_accounts(account_id),
    verified_hours DECIMAL(8, 2) NOT NULL CHECK (verified_hours >= 0.0),
    hourly_rate DECIMAL(6, 2) NOT NULL CHECK (hourly_rate > 0.0),
    gross_amount DECIMAL(10, 2) NOT NULL CHECK (gross_amount >= 0.0),
    admin_fee DECIMAL(10, 2) DEFAULT 0.0 CHECK (admin_fee >= 0.0),
    net_amount DECIMAL(10, 2) NOT NULL CHECK (net_amount >= 0.0),
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Session references
    session_ids JSONB DEFAULT '[]'::jsonb,
    blockchain_references JSONB DEFAULT '[]'::jsonb
);

-- Blockchain records for credit transactions
CREATE TABLE credit_blockchain_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(20) CHECK (entity_type IN ('session', 'transaction', 'disbursement')),
    entity_id UUID NOT NULL,
    blockchain_hash VARCHAR(255) NOT NULL,
    block_number INTEGER NOT NULL CHECK (block_number >= 0),
    network VARCHAR(20) DEFAULT 'solana',
    gas_used INTEGER CHECK (gas_used >= 0),
    gas_price DECIMAL(12, 8) CHECK (gas_price >= 0.0),
    transaction_fee DECIMAL(12, 8) CHECK (transaction_fee >= 0.0),
    confirmations INTEGER DEFAULT 0 CHECK (confirmations >= 0),
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(blockchain_hash)
);

-- Add triggers for updated_at
CREATE TRIGGER update_credit_accounts_updated_at BEFORE UPDATE ON credit_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_institution_accounts_updated_at BEFORE UPDATE ON institution_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate available balance
CREATE OR REPLACE FUNCTION calculate_available_balance(account_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    account_record credit_accounts%ROWTYPE;
BEGIN
    SELECT * INTO account_record FROM credit_accounts WHERE account_id = account_uuid;
    
    IF NOT FOUND THEN
        RETURN 0.0;
    END IF;
    
    RETURN GREATEST(0.0, account_record.total_credits_earned - account_record.total_credits_disbursed - account_record.pending_credits);
END;
$$ LANGUAGE plpgsql;

-- Function to update account balances
CREATE OR REPLACE FUNCTION update_account_balance(account_uuid UUID)
RETURNS void AS $$
DECLARE
    total_earned DECIMAL(12, 2) := 0.0;
    total_disbursed DECIMAL(12, 2) := 0.0;
    total_pending DECIMAL(12, 2) := 0.0;
BEGIN
    -- Calculate totals from transactions
    SELECT 
        COALESCE(SUM(CASE WHEN transaction_type = 'earned' AND status = 'completed' THEN amount ELSE 0 END), 0.0),
        COALESCE(SUM(CASE WHEN transaction_type = 'disbursed' AND status = 'completed' THEN amount ELSE 0 END), 0.0),
        COALESCE(SUM(CASE WHEN status IN ('pending', 'processing') THEN amount ELSE 0 END), 0.0)
    INTO total_earned, total_disbursed, total_pending
    FROM credit_transactions 
    WHERE account_id = account_uuid;
    
    -- Update account
    UPDATE credit_accounts 
    SET 
        total_credits_earned = total_earned,
        total_credits_disbursed = total_disbursed,
        pending_credits = total_pending,
        available_balance = calculate_available_balance(account_uuid),
        updated_at = CURRENT_TIMESTAMP
    WHERE account_id = account_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to validate disbursement split percentages
CREATE OR REPLACE FUNCTION validate_disbursement_split(split_json JSONB)
RETURNS BOOLEAN AS $$
DECLARE
    total_percentage DECIMAL := 0.0;
    key TEXT;
    value JSONB;
BEGIN
    FOR key, value IN SELECT * FROM jsonb_each(split_json) LOOP
        total_percentage := total_percentage + (value::text)::DECIMAL;
    END LOOP;
    
    RETURN ABS(total_percentage - 100.0) < 0.01; -- Allow small floating point errors
END;
$$ LANGUAGE plpgsql;

-- Add constraint to validate disbursement split
ALTER TABLE credit_accounts 
ADD CONSTRAINT check_disbursement_split 
CHECK (validate_disbursement_split(default_disbursement_split));