-- CareCred Database Indexes and Performance Optimizations

-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_university ON users(university) WHERE user_type = 'student';
CREATE INDEX idx_users_student_id ON users(student_id) WHERE user_type = 'student';
CREATE INDEX idx_users_location ON users(city, state, zip_code) WHERE user_type = 'senior';
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_rating ON users(rating) WHERE rating > 0;

-- User tokens indexes
CREATE INDEX idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX idx_user_tokens_type ON user_tokens(token_type);
CREATE INDEX idx_user_tokens_expires_at ON user_tokens(expires_at);
CREATE INDEX idx_user_tokens_revoked ON user_tokens(revoked) WHERE revoked = FALSE;

-- User verification documents indexes
CREATE INDEX idx_verification_docs_user_id ON user_verification_documents(user_id);
CREATE INDEX idx_verification_docs_status ON user_verification_documents(verification_status);
CREATE INDEX idx_verification_docs_uploaded_at ON user_verification_documents(uploaded_at);

-- User availability indexes
CREATE INDEX idx_user_availability_user_id ON user_availability(user_id);
CREATE INDEX idx_user_availability_day_time ON user_availability(day_of_week, start_time, end_time);
CREATE INDEX idx_user_availability_active ON user_availability(is_active) WHERE is_active = TRUE;

-- GPS locations indexes
CREATE INDEX idx_gps_locations_coordinates ON gps_locations(latitude, longitude);
CREATE INDEX idx_gps_locations_timestamp ON gps_locations(timestamp);
CREATE INDEX idx_gps_locations_accuracy ON gps_locations(accuracy);

-- Sessions table indexes
CREATE INDEX idx_sessions_student_id ON sessions(student_id);
CREATE INDEX idx_sessions_senior_id ON sessions(senior_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_type ON sessions(session_type);
CREATE INDEX idx_sessions_scheduled_start ON sessions(scheduled_start_time);
CREATE INDEX idx_sessions_actual_start ON sessions(actual_start_time);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_location ON sessions(location_id);
CREATE INDEX idx_sessions_blockchain_verified ON sessions(blockchain_verified);
CREATE INDEX idx_sessions_credit_disbursed ON sessions(credit_disbursed);

-- Composite indexes for common queries
CREATE INDEX idx_sessions_student_status ON sessions(student_id, status);
CREATE INDEX idx_sessions_senior_status ON sessions(senior_id, status);
CREATE INDEX idx_sessions_date_range ON sessions(actual_start_time, actual_end_time) WHERE actual_start_time IS NOT NULL;

-- Session requests indexes
CREATE INDEX idx_session_requests_student_id ON session_requests(student_id);
CREATE INDEX idx_session_requests_senior_id ON session_requests(senior_id);
CREATE INDEX idx_session_requests_status ON session_requests(status);
CREATE INDEX idx_session_requests_preferred_date ON session_requests(preferred_date);
CREATE INDEX idx_session_requests_expires_at ON session_requests(expires_at);

-- Session alerts indexes
CREATE INDEX idx_session_alerts_session_id ON session_alerts(session_id);
CREATE INDEX idx_session_alerts_severity ON session_alerts(severity);
CREATE INDEX idx_session_alerts_resolved ON session_alerts(resolved);
CREATE INDEX idx_session_alerts_created_at ON session_alerts(created_at);

-- Session GPS tracking indexes
CREATE INDEX idx_session_gps_tracking_session_id ON session_gps_tracking(session_id);
CREATE INDEX idx_session_gps_tracking_user_id ON session_gps_tracking(user_id);
CREATE INDEX idx_session_gps_tracking_recorded_at ON session_gps_tracking(recorded_at);

-- Credit accounts indexes
CREATE INDEX idx_credit_accounts_student_id ON credit_accounts(student_id);
CREATE INDEX idx_credit_accounts_available_balance ON credit_accounts(available_balance);
CREATE INDEX idx_credit_accounts_institution ON credit_accounts(institution_name);

-- Credit transactions indexes
CREATE INDEX idx_credit_transactions_account_id ON credit_transactions(account_id);
CREATE INDEX idx_credit_transactions_student_id ON credit_transactions(student_id);
CREATE INDEX idx_credit_transactions_session_id ON credit_transactions(session_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(transaction_type);
CREATE INDEX idx_credit_transactions_status ON credit_transactions(status);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);
CREATE INDEX idx_credit_transactions_blockchain_verified ON credit_transactions(blockchain_verified);

-- Credit disbursements indexes
CREATE INDEX idx_credit_disbursements_student_id ON credit_disbursements(student_id);
CREATE INDEX idx_credit_disbursements_account_id ON credit_disbursements(account_id);
CREATE INDEX idx_credit_disbursements_institution_id ON credit_disbursements(institution_id);
CREATE INDEX idx_credit_disbursements_status ON credit_disbursements(status);
CREATE INDEX idx_credit_disbursements_requested_at ON credit_disbursements(requested_at);

-- Government payments indexes
CREATE INDEX idx_government_payments_status ON government_payments(status);
CREATE INDEX idx_government_payments_payment_date ON government_payments(payment_date);
CREATE INDEX idx_government_payments_period ON government_payments(report_period_start, report_period_end);

-- Payment allocations indexes
CREATE INDEX idx_payment_allocations_payment_id ON payment_allocations(payment_id);
CREATE INDEX idx_payment_allocations_student_id ON payment_allocations(student_id);
CREATE INDEX idx_payment_allocations_account_id ON payment_allocations(account_id);

-- Blockchain session logs indexes
CREATE INDEX idx_blockchain_session_logs_session_id ON blockchain_session_logs(session_id);
CREATE INDEX idx_blockchain_session_logs_hash ON blockchain_session_logs(session_hash);
CREATE INDEX idx_blockchain_session_logs_start_time ON blockchain_session_logs(start_time);
CREATE INDEX idx_blockchain_session_logs_task_type ON blockchain_session_logs(task_type);

-- Blockchain transactions indexes
CREATE INDEX idx_blockchain_transactions_signature ON blockchain_transactions(solana_transaction_signature);
CREATE INDEX idx_blockchain_transactions_block_number ON blockchain_transactions(block_number);
CREATE INDEX idx_blockchain_transactions_status ON blockchain_transactions(status);
CREATE INDEX idx_blockchain_transactions_session_log ON blockchain_transactions(session_log_id);
CREATE INDEX idx_blockchain_transactions_timestamp ON blockchain_transactions(timestamp);

-- Signature requests indexes
CREATE INDEX idx_signature_requests_session_id ON signature_requests(session_id);
CREATE INDEX idx_signature_requests_student_id ON signature_requests(student_id);
CREATE INDEX idx_signature_requests_senior_id ON signature_requests(senior_id);
CREATE INDEX idx_signature_requests_status ON signature_requests(status);
CREATE INDEX idx_signature_requests_expires_at ON signature_requests(expires_at);

-- Verification results indexes
CREATE INDEX idx_verification_results_session_id ON verification_results(session_id);
CREATE INDEX idx_verification_results_transaction_id ON verification_results(transaction_id);
CREATE INDEX idx_verification_results_verified ON verification_results(is_verified);
CREATE INDEX idx_verification_results_timestamp ON verification_results(verification_timestamp);

-- Conversations indexes
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_active ON conversations(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_conversations_priority ON conversations(priority_level);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at);

-- Conversation participants indexes
CREATE INDEX idx_conversation_participants_conversation ON conversation_participants(conversation_id);
CREATE INDEX idx_conversation_participants_user ON conversation_participants(user_id);
CREATE INDEX idx_conversation_participants_active ON conversation_participants(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_conversation_participants_unread ON conversation_participants(unread_count) WHERE unread_count > 0;

-- Messages indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
CREATE INDEX idx_messages_type ON messages(message_type);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_flagged ON messages(is_flagged) WHERE is_flagged = TRUE;
CREATE INDEX idx_messages_system ON messages(is_system_message) WHERE is_system_message = TRUE;

-- Message read receipts indexes
CREATE INDEX idx_message_read_receipts_message ON message_read_receipts(message_id);
CREATE INDEX idx_message_read_receipts_user ON message_read_receipts(user_id);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_sent ON notifications(is_sent);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_expires_at ON notifications(expires_at);

-- Emergency alerts indexes
CREATE INDEX idx_emergency_alerts_initiated_by ON emergency_alerts(initiated_by);
CREATE INDEX idx_emergency_alerts_session_id ON emergency_alerts(session_id);
CREATE INDEX idx_emergency_alerts_severity ON emergency_alerts(severity);
CREATE INDEX idx_emergency_alerts_active ON emergency_alerts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_emergency_alerts_created_at ON emergency_alerts(created_at);

-- Notification delivery log indexes
CREATE INDEX idx_notification_delivery_notification ON notification_delivery_log(notification_id);
CREATE INDEX idx_notification_delivery_channel ON notification_delivery_log(channel);
CREATE INDEX idx_notification_delivery_status ON notification_delivery_log(status);
CREATE INDEX idx_notification_delivery_attempted_at ON notification_delivery_log(attempted_at);

-- Additional performance indexes for common query patterns
CREATE INDEX idx_users_active_students ON users(user_id, university, status) 
    WHERE user_type = 'student' AND status = 'approved';

CREATE INDEX idx_users_active_seniors ON users(user_id, city, state, status) 
    WHERE user_type = 'senior' AND status = 'approved';

CREATE INDEX idx_sessions_pending_completion ON sessions(session_id, status, actual_end_time) 
    WHERE status IN ('checked_in', 'in_progress');

CREATE INDEX idx_sessions_ready_for_blockchain ON sessions(session_id, status, blockchain_verified) 
    WHERE status = 'completed' AND blockchain_verified = FALSE;

CREATE INDEX idx_credit_transactions_pending ON credit_transactions(transaction_id, status, created_at) 
    WHERE status = 'pending';

CREATE INDEX idx_notifications_unread_recent ON notifications(user_id, created_at) 
    WHERE is_read = FALSE AND created_at > (CURRENT_TIMESTAMP - INTERVAL '30 days');

-- Partial indexes for frequently filtered data
CREATE INDEX idx_sessions_active_date_range ON sessions(actual_start_time) 
    WHERE status IN ('scheduled', 'checked_in', 'in_progress', 'completed')
    AND actual_start_time > (CURRENT_TIMESTAMP - INTERVAL '6 months');

CREATE INDEX idx_messages_recent_conversations ON messages(conversation_id, sent_at) 
    WHERE sent_at > (CURRENT_TIMESTAMP - INTERVAL '3 months');

-- Cleanup indexes for maintenance operations
CREATE INDEX idx_user_tokens_expired ON user_tokens(expires_at) 
    WHERE revoked = FALSE AND expires_at < CURRENT_TIMESTAMP;

CREATE INDEX idx_session_requests_expired ON session_requests(expires_at) 
    WHERE status = 'pending' AND expires_at < CURRENT_TIMESTAMP;

CREATE INDEX idx_notifications_old ON notifications(created_at) 
    WHERE is_read = TRUE AND created_at < (CURRENT_TIMESTAMP - INTERVAL '90 days');

-- Foreign key constraints with proper naming
ALTER TABLE user_tokens 
    ADD CONSTRAINT fk_user_tokens_user_id 
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

ALTER TABLE user_verification_documents 
    ADD CONSTRAINT fk_verification_docs_user_id 
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

ALTER TABLE user_availability 
    ADD CONSTRAINT fk_user_availability_user_id 
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

ALTER TABLE sessions 
    ADD CONSTRAINT fk_sessions_student_id 
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    ADD CONSTRAINT fk_sessions_senior_id 
    FOREIGN KEY (senior_id) REFERENCES users(user_id);

ALTER TABLE credit_transactions 
    ADD CONSTRAINT fk_credit_transactions_account_id 
    FOREIGN KEY (account_id) REFERENCES credit_accounts(account_id) ON DELETE CASCADE;

-- Check constraints for data integrity
ALTER TABLE users 
    ADD CONSTRAINT check_user_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users 
    ADD CONSTRAINT check_phone_format 
    CHECK (phone IS NULL OR phone ~* '^\+?[1-9]\d{1,14}$');

ALTER TABLE sessions 
    ADD CONSTRAINT check_session_duration 
    CHECK (estimated_duration_hours > 0 AND estimated_duration_hours <= 24);

ALTER TABLE credit_transactions 
    ADD CONSTRAINT check_transaction_amount 
    CHECK (amount > 0);

ALTER TABLE gps_locations 
    ADD CONSTRAINT check_gps_coordinates 
    CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180);

-- Unique constraints for data integrity
ALTER TABLE users 
    ADD CONSTRAINT unique_student_id_per_university 
    UNIQUE (university, student_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE credit_accounts 
    ADD CONSTRAINT unique_credit_account_per_student 
    UNIQUE (student_id);

ALTER TABLE blockchain_session_logs 
    ADD CONSTRAINT unique_session_hash 
    UNIQUE (session_hash);

-- Create materialized views for common aggregations
CREATE MATERIALIZED VIEW user_session_stats AS
SELECT 
    u.user_id,
    u.user_type,
    COUNT(s.session_id) as total_sessions,
    AVG(s.actual_duration_hours) as avg_session_duration,
    SUM(s.credit_amount) as total_credits,
    AVG(CASE WHEN u.user_type = 'student' THEN s.senior_rating 
             ELSE s.student_rating END) as avg_rating,
    MAX(s.actual_end_time) as last_session_date
FROM users u
LEFT JOIN sessions s ON (
    (u.user_type = 'student' AND u.user_id = s.student_id) OR
    (u.user_type = 'senior' AND u.user_id = s.senior_id)
)
WHERE s.status = 'completed'
GROUP BY u.user_id, u.user_type;

CREATE UNIQUE INDEX idx_user_session_stats_user_id ON user_session_stats(user_id);

-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_session_stats;
END;
$$ LANGUAGE plpgsql;

-- Create function for database maintenance
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Clean up expired tokens
    DELETE FROM user_tokens 
    WHERE expires_at < CURRENT_TIMESTAMP AND revoked = FALSE;
    
    -- Clean up expired session requests
    UPDATE session_requests 
    SET status = 'expired' 
    WHERE status = 'pending' AND expires_at < CURRENT_TIMESTAMP;
    
    -- Clean up old read notifications
    DELETE FROM notifications 
    WHERE is_read = TRUE 
    AND created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- Clean up old notification delivery logs
    DELETE FROM notification_delivery_log 
    WHERE attempted_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- Update statistics
    ANALYZE;
END;
$$ LANGUAGE plpgsql;

-- Performance monitoring queries (commented for documentation)
/*
-- Find slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Monitor index usage
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_tup_read = 0;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
*/