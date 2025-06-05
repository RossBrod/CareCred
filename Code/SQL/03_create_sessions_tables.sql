-- CareCred Sessions and GPS Tracking Tables

-- GPS locations table for reusable location data
CREATE TABLE gps_locations (
    location_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    latitude DECIMAL(10, 8) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
    longitude DECIMAL(11, 8) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
    accuracy DECIMAL(8, 2) NOT NULL CHECK (accuracy >= 0.0 AND accuracy <= 1000.0),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Main sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(user_id),
    senior_id UUID NOT NULL REFERENCES users(user_id),
    session_type session_type NOT NULL,
    status session_status DEFAULT 'requested',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Scheduling
    scheduled_start_time TIMESTAMP WITH TIME ZONE,
    scheduled_end_time TIMESTAMP WITH TIME ZONE,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    estimated_duration_hours DECIMAL(4, 2) NOT NULL CHECK (estimated_duration_hours > 0 AND estimated_duration_hours <= 24),
    actual_duration_hours DECIMAL(4, 2) CHECK (actual_duration_hours >= 0 AND actual_duration_hours <= 24),
    
    -- Location
    location_id UUID REFERENCES gps_locations(location_id),
    senior_address TEXT NOT NULL,
    special_instructions TEXT,
    
    -- Check-in/Check-out tracking
    check_in_location_id UUID REFERENCES gps_locations(location_id),
    check_out_location_id UUID REFERENCES gps_locations(location_id),
    check_in_time TIMESTAMP WITH TIME ZONE,
    check_out_time TIMESTAMP WITH TIME ZONE,
    
    -- Ratings and reviews
    student_rating INTEGER CHECK (student_rating >= 1 AND student_rating <= 5),
    senior_rating INTEGER CHECK (senior_rating >= 1 AND senior_rating <= 5),
    student_review TEXT,
    senior_review TEXT,
    
    -- Blockchain and verification
    blockchain_transaction_hash VARCHAR(255),
    blockchain_block_number INTEGER,
    blockchain_confirmations INTEGER DEFAULT 0,
    verification_status VARCHAR(20) DEFAULT 'pending',
    signature_request_id UUID,
    student_signature TEXT,
    senior_signature TEXT,
    session_hash VARCHAR(255),
    blockchain_verified BOOLEAN DEFAULT FALSE,
    blockchain_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Credit calculation
    credit_amount DECIMAL(10, 2) CHECK (credit_amount >= 0.0),
    hourly_rate DECIMAL(6, 2) DEFAULT 15.00 CHECK (hourly_rate > 0.0 AND hourly_rate <= 100.0),
    credit_disbursed BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_scheduled_times CHECK (
        scheduled_end_time IS NULL OR scheduled_start_time IS NULL OR 
        scheduled_end_time > scheduled_start_time
    ),
    CONSTRAINT check_actual_times CHECK (
        actual_end_time IS NULL OR actual_start_time IS NULL OR 
        actual_end_time > actual_start_time
    ),
    CONSTRAINT check_student_senior_different CHECK (student_id != senior_id)
);

-- Session requests (before they become full sessions)
CREATE TABLE session_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(user_id),
    senior_id UUID NOT NULL REFERENCES users(user_id),
    session_type session_type NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time_start TIME NOT NULL,
    preferred_time_end TIME NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    response_message TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '72 hours'),
    
    CONSTRAINT check_time_range CHECK (preferred_time_end > preferred_time_start),
    CONSTRAINT check_student_senior_different CHECK (student_id != senior_id)
);

-- Session alerts and notifications
CREATE TABLE session_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('overtime', 'gps_drift', 'no_checkin', 'emergency', 'inactivity')),
    severity alert_severity NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id),
    resolution_notes TEXT
);

-- Session photos (for verification)
CREATE TABLE session_photos (
    photo_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    photo_url TEXT NOT NULL,
    photo_type VARCHAR(20) CHECK (photo_type IN ('check_in', 'check_out', 'during_session', 'verification')),
    location_id UUID REFERENCES gps_locations(location_id),
    taken_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    mime_type VARCHAR(100)
);

-- Session timeline for audit trail
CREATE TABLE session_timeline (
    timeline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    event_data JSONB,
    user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Session cancellation reasons
CREATE TABLE session_cancellations (
    cancellation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    cancelled_by UUID NOT NULL REFERENCES users(user_id),
    cancellation_reason VARCHAR(100) NOT NULL,
    detailed_reason TEXT,
    cancelled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    refund_required BOOLEAN DEFAULT FALSE,
    penalty_applied BOOLEAN DEFAULT FALSE
);

-- GPS tracking history for sessions
CREATE TABLE session_gps_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    location_id UUID NOT NULL REFERENCES gps_locations(location_id),
    tracking_type VARCHAR(20) CHECK (tracking_type IN ('check_in', 'check_out', 'periodic', 'alert')),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    device_info JSONB
);

-- Add triggers for updated_at
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-expire session requests
CREATE OR REPLACE FUNCTION expire_old_session_requests()
RETURNS void AS $$
BEGIN
    UPDATE session_requests 
    SET status = 'expired' 
    WHERE status = 'pending' 
    AND expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate session duration
CREATE OR REPLACE FUNCTION calculate_session_duration(
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE
) RETURNS DECIMAL AS $$
BEGIN
    IF start_time IS NULL OR end_time IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN EXTRACT(EPOCH FROM (end_time - start_time)) / 3600.0;
END;
$$ LANGUAGE plpgsql;

-- Function to validate GPS location within reasonable distance
CREATE OR REPLACE FUNCTION validate_gps_distance(
    lat1 DECIMAL, lon1 DECIMAL, 
    lat2 DECIMAL, lon2 DECIMAL, 
    max_distance_meters INTEGER DEFAULT 100
) RETURNS BOOLEAN AS $$
DECLARE
    distance_meters DECIMAL;
BEGIN
    -- Calculate distance using Haversine formula (simplified)
    distance_meters := 6371000 * acos(
        cos(radians(lat1)) * cos(radians(lat2)) * 
        cos(radians(lon2) - radians(lon1)) + 
        sin(radians(lat1)) * sin(radians(lat2))
    );
    
    RETURN distance_meters <= max_distance_meters;
END;
$$ LANGUAGE plpgsql;