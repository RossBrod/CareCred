-- CareCred Blockchain Logging Tables

-- Session logs that get recorded on blockchain
CREATE TABLE blockchain_session_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    student_id_hash VARCHAR(255) NOT NULL, -- Hashed for privacy
    senior_id_hash VARCHAR(255) NOT NULL, -- Hashed for privacy
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER NOT NULL CHECK (duration > 0), -- Duration in minutes
    location_hash VARCHAR(255) NOT NULL, -- Hashed location data
    task_type task_type NOT NULL,
    student_signature TEXT NOT NULL,
    senior_signature TEXT NOT NULL,
    session_hash VARCHAR(255) NOT NULL UNIQUE, -- Unique hash of session data
    credit_amount DECIMAL(10, 2) NOT NULL CHECK (credit_amount >= 0.0),
    verification_level VARCHAR(20) DEFAULT 'standard',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_session_duration CHECK (end_time > start_time)
);

-- Blockchain transactions for session logs
CREATE TABLE blockchain_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    solana_transaction_signature VARCHAR(255) NOT NULL UNIQUE, -- Solana transaction signature
    block_hash VARCHAR(255) NOT NULL,
    block_number INTEGER NOT NULL CHECK (block_number >= 0),
    transaction_index INTEGER NOT NULL CHECK (transaction_index >= 0),
    from_address VARCHAR(100) NOT NULL,
    to_address VARCHAR(100) NOT NULL,
    gas_used INTEGER NOT NULL CHECK (gas_used >= 0),
    gas_price DECIMAL(12, 8) NOT NULL CHECK (gas_price >= 0.0),
    transaction_fee DECIMAL(12, 8) NOT NULL CHECK (transaction_fee >= 0.0),
    status transaction_status DEFAULT 'pending',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    confirmations INTEGER DEFAULT 0 CHECK (confirmations >= 0),
    
    -- Linked session log
    session_log_id UUID REFERENCES blockchain_session_logs(log_id) ON DELETE CASCADE,
    
    -- Retry and error handling
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Digital signature requests for sessions
CREATE TABLE signature_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(user_id),
    senior_id UUID NOT NULL REFERENCES users(user_id),
    session_data_hash VARCHAR(255) NOT NULL, -- Hash of session data to be signed
    
    -- Signatures
    student_signature TEXT,
    senior_signature TEXT,
    student_signed_at TIMESTAMP WITH TIME ZONE,
    senior_signed_at TIMESTAMP WITH TIME ZONE,
    
    status signature_status DEFAULT 'pending',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    notification_sent BOOLEAN DEFAULT FALSE
);

-- Blockchain verification results
CREATE TABLE verification_results (
    verification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES blockchain_transactions(transaction_id),
    is_verified BOOLEAN NOT NULL,
    verification_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    block_number INTEGER CHECK (block_number >= 0),
    confirmations INTEGER DEFAULT 0 CHECK (confirmations >= 0),
    integrity_check BOOLEAN NOT NULL,
    signatures_valid BOOLEAN NOT NULL,
    credit_eligible BOOLEAN NOT NULL,
    verification_details JSONB DEFAULT '{}'::jsonb,
    public_proof_url TEXT,
    verified_by VARCHAR(100) NOT NULL, -- Verification service identifier
    error_details JSONB DEFAULT '[]'::jsonb
);

-- Blockchain configuration settings
CREATE TABLE blockchain_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    network VARCHAR(20) DEFAULT 'devnet' CHECK (network IN ('mainnet', 'testnet', 'devnet')),
    rpc_endpoint TEXT NOT NULL,
    program_id VARCHAR(100) NOT NULL,
    payer_keypair_path TEXT NOT NULL,
    commitment_level VARCHAR(20) DEFAULT 'confirmed' CHECK (commitment_level IN ('processed', 'confirmed', 'finalized')),
    max_retries INTEGER DEFAULT 3 CHECK (max_retries >= 0),
    timeout_seconds INTEGER DEFAULT 30 CHECK (timeout_seconds > 0),
    gas_limit INTEGER DEFAULT 200000 CHECK (gas_limit > 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Signature collection workflow
CREATE TABLE signature_collection_requests (
    collection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    require_both_signatures BOOLEAN DEFAULT TRUE,
    signature_timeout_hours INTEGER DEFAULT 24 CHECK (signature_timeout_hours > 0),
    send_notifications BOOLEAN DEFAULT TRUE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'collecting', 'completed', 'expired', 'failed'))
);

-- Blockchain health monitoring
CREATE TABLE blockchain_health_checks (
    check_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    network_status VARCHAR(20) NOT NULL,
    rpc_latency_ms DECIMAL(8, 2) NOT NULL CHECK (rpc_latency_ms >= 0.0),
    last_block_number INTEGER NOT NULL CHECK (last_block_number >= 0),
    last_block_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    program_status VARCHAR(20) NOT NULL,
    wallet_balance DECIMAL(15, 8) NOT NULL CHECK (wallet_balance >= 0.0),
    pending_transactions INTEGER DEFAULT 0 CHECK (pending_transactions >= 0),
    failed_transactions_24h INTEGER DEFAULT 0 CHECK (failed_transactions_24h >= 0),
    average_confirmation_time_ms DECIMAL(10, 2) CHECK (average_confirmation_time_ms >= 0.0),
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Blockchain audit trail
CREATE TABLE blockchain_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation_type VARCHAR(50) NOT NULL,
    session_id UUID REFERENCES sessions(session_id),
    transaction_id UUID REFERENCES blockchain_transactions(transaction_id),
    user_id UUID REFERENCES users(user_id),
    operation_details JSONB NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER CHECK (execution_time_ms >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add triggers for updated_at
CREATE TRIGGER update_blockchain_config_updated_at BEFORE UPDATE ON blockchain_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate session hash
CREATE OR REPLACE FUNCTION generate_session_hash(
    p_session_id UUID,
    p_student_id_hash VARCHAR,
    p_senior_id_hash VARCHAR,
    p_start_time TIMESTAMP WITH TIME ZONE,
    p_end_time TIMESTAMP WITH TIME ZONE,
    p_location_hash VARCHAR,
    p_task_type task_type
) RETURNS VARCHAR AS $$
DECLARE
    hash_input TEXT;
    session_hash VARCHAR;
BEGIN
    hash_input := CONCAT(
        p_session_id::TEXT, '|',
        p_student_id_hash, '|',
        p_senior_id_hash, '|',
        EXTRACT(EPOCH FROM p_start_time)::TEXT, '|',
        EXTRACT(EPOCH FROM p_end_time)::TEXT, '|',
        p_location_hash, '|',
        p_task_type::TEXT
    );
    
    session_hash := encode(digest(hash_input, 'sha256'), 'hex');
    RETURN session_hash;
END;
$$ LANGUAGE plpgsql;

-- Function to validate signatures
CREATE OR REPLACE FUNCTION validate_digital_signature(
    signature_text TEXT,
    data_hash VARCHAR,
    public_key TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    -- In a real implementation, this would verify the digital signature
    -- For now, we'll do basic validation
    RETURN signature_text IS NOT NULL 
           AND LENGTH(signature_text) > 20 
           AND data_hash IS NOT NULL 
           AND public_key IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to check if session is ready for blockchain logging
CREATE OR REPLACE FUNCTION is_session_ready_for_blockchain(p_session_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    session_record sessions%ROWTYPE;
    signature_record signature_requests%ROWTYPE;
BEGIN
    -- Get session details
    SELECT * INTO session_record FROM sessions WHERE session_id = p_session_id;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Check if session is completed
    IF session_record.status != 'completed' THEN
        RETURN FALSE;
    END IF;
    
    -- Check if both signatures are collected
    SELECT * INTO signature_record 
    FROM signature_requests 
    WHERE session_id = p_session_id 
    AND status = 'collected';
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Validate signatures exist
    IF signature_record.student_signature IS NULL OR signature_record.senior_signature IS NULL THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to create blockchain session log from session
CREATE OR REPLACE FUNCTION create_blockchain_session_log(p_session_id UUID)
RETURNS UUID AS $$
DECLARE
    session_record sessions%ROWTYPE;
    log_id UUID;
    student_hash VARCHAR;
    senior_hash VARCHAR;
    location_hash VARCHAR;
    session_hash VARCHAR;
BEGIN
    -- Get session details
    SELECT * INTO session_record FROM sessions WHERE session_id = p_session_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Session not found: %', p_session_id;
    END IF;
    
    -- Generate hashes for privacy
    student_hash := encode(digest(session_record.student_id::TEXT, 'sha256'), 'hex');
    senior_hash := encode(digest(session_record.senior_id::TEXT, 'sha256'), 'hex');
    location_hash := encode(digest(session_record.senior_address, 'sha256'), 'hex');
    
    -- Generate session hash
    session_hash := generate_session_hash(
        p_session_id,
        student_hash,
        senior_hash,
        session_record.actual_start_time,
        session_record.actual_end_time,
        location_hash,
        session_record.session_type
    );
    
    -- Insert blockchain session log
    INSERT INTO blockchain_session_logs (
        session_id,
        student_id_hash,
        senior_id_hash,
        start_time,
        end_time,
        duration,
        location_hash,
        task_type,
        student_signature,
        senior_signature,
        session_hash,
        credit_amount
    ) VALUES (
        p_session_id,
        student_hash,
        senior_hash,
        session_record.actual_start_time,
        session_record.actual_end_time,
        EXTRACT(EPOCH FROM (session_record.actual_end_time - session_record.actual_start_time)) / 60,
        location_hash,
        session_record.session_type::task_type,
        session_record.student_signature,
        session_record.senior_signature,
        session_hash,
        session_record.credit_amount
    ) RETURNING log_id INTO log_id;
    
    RETURN log_id;
END;
$$ LANGUAGE plpgsql;