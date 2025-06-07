-- CareCred Session Management Tables - Normalized
-- Proper separation of concerns with meaningful relationships

-- =====================================================
-- LOCATION AND GPS TRACKING
-- =====================================================

-- GPS locations for reusable location data
CREATE TABLE gps_locations (
    location_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    latitude DECIMAL(10, 8) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
    longitude DECIMAL(11, 8) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
    accuracy_meters DECIMAL(8, 2) NOT NULL CHECK (accuracy_meters >= 0.0 AND accuracy_meters <= 1000.0),
    altitude_meters DECIMAL(8, 2),
    
    -- PostGIS point for spatial queries
    location_point GEOMETRY(POINT, 4326),
    
    -- Address information (reverse geocoded or provided)
    street_address VARCHAR(200),
    city VARCHAR(100),
    state_id INTEGER REFERENCES states(state_id),
    zip_code VARCHAR(10),
    
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CORE SESSION TABLES
-- =====================================================

-- Main sessions table - core session data only
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student_profiles(user_id),
    senior_id UUID NOT NULL REFERENCES senior_profiles(user_id),
    service_type_id UUID NOT NULL REFERENCES service_types(service_type_id),
    
    -- Session identification
    session_number VARCHAR(20) UNIQUE, -- Human-readable session number (auto-generated)
    title VARCHAR(200) NOT NULL,
    description TEXT CHECK (LENGTH(description) <= 2000),
    status session_status DEFAULT 'requested',
    
    -- Scheduling information
    scheduled_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_duration_hours DECIMAL(4, 2) NOT NULL CHECK (estimated_duration_hours > 0 AND estimated_duration_hours <= 24),
    
    -- Actual timing (set during session execution)
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    actual_duration_hours DECIMAL(4, 2) CHECK (actual_duration_hours >= 0),
    
    -- Location reference
    location_id UUID REFERENCES gps_locations(location_id),
    special_instructions TEXT CHECK (LENGTH(special_instructions) <= 1000),
    
    -- Session completion and verification
    completion_notes TEXT,
    requires_admin_review BOOLEAN DEFAULT FALSE,
    admin_review_notes TEXT,
    reviewed_by UUID REFERENCES admin_profiles(user_id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Business rule constraints
    CONSTRAINT check_scheduled_times CHECK (scheduled_end_time > scheduled_start_time),
    CONSTRAINT check_actual_times CHECK (
        actual_end_time IS NULL OR actual_start_time IS NULL OR 
        actual_end_time > actual_start_time
    ),
    CONSTRAINT check_different_users CHECK (student_id != senior_id)
);

-- Session requests (pre-session workflow)
CREATE TABLE session_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student_profiles(user_id),
    senior_id UUID NOT NULL REFERENCES senior_profiles(user_id),
    service_type_id UUID NOT NULL REFERENCES service_types(service_type_id),
    
    -- Request details
    preferred_date DATE NOT NULL,
    preferred_time_start TIME NOT NULL,
    preferred_time_end TIME NOT NULL,
    message TEXT CHECK (LENGTH(message) <= 1000),
    urgency_level VARCHAR(20) DEFAULT 'normal' CHECK (urgency_level IN ('low', 'normal', 'high', 'urgent')),
    
    -- Request lifecycle
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'converted')),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '72 hours'),
    
    -- Response tracking
    response_message TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,
    responded_by UUID REFERENCES users(user_id), -- Could be senior or admin
    
    -- Conversion to session
    session_id UUID REFERENCES sessions(session_id), -- Set when converted to actual session
    
    CONSTRAINT check_time_range CHECK (preferred_time_end > preferred_time_start),
    CONSTRAINT check_different_users CHECK (student_id != senior_id)
);

-- =====================================================
-- SESSION TRACKING AND MONITORING
-- =====================================================

-- Session check-ins and check-outs
CREATE TABLE session_checkins (
    checkin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    checkin_type VARCHAR(20) NOT NULL CHECK (checkin_type IN ('check_in', 'check_out', 'safety_check')),
    
    -- Location verification
    location_id UUID NOT NULL REFERENCES gps_locations(location_id),
    distance_from_scheduled_meters DECIMAL(10, 2), -- Distance from planned location
    location_verified BOOLEAN DEFAULT FALSE,
    
    -- Timing
    checkin_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_on_time BOOLEAN DEFAULT TRUE,
    minutes_early_late INTEGER DEFAULT 0, -- Negative for early, positive for late
    
    -- Device and security
    device_fingerprint VARCHAR(255),
    ip_address INET,
    verification_method VARCHAR(20) DEFAULT 'gps', -- gps, qr_code, manual
    
    -- Photo verification
    photo_url TEXT,
    photo_verified BOOLEAN DEFAULT FALSE,
    
    notes TEXT
);

-- Session GPS tracking history
CREATE TABLE session_gps_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    location_id UUID NOT NULL REFERENCES gps_locations(location_id),
    
    tracking_type VARCHAR(20) NOT NULL CHECK (tracking_type IN ('periodic', 'manual', 'emergency', 'departure')),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Movement tracking
    speed_mph DECIMAL(5, 2), -- For safety monitoring
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    
    -- Device information
    device_info JSONB DEFAULT '{}'::jsonb,
    
    -- Safety flags
    is_emergency_location BOOLEAN DEFAULT FALSE,
    triggered_alert BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- SESSION COMPLETION AND FEEDBACK
-- =====================================================

-- Session ratings and reviews (separate from main session table)
CREATE TABLE session_ratings (
    rating_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    
    -- Student rating of senior
    student_rating_senior INTEGER CHECK (student_rating_senior >= 1 AND student_rating_senior <= 5),
    student_review_senior TEXT CHECK (LENGTH(student_review_senior) <= 1000),
    student_would_recommend BOOLEAN,
    student_rated_at TIMESTAMP WITH TIME ZONE,
    
    -- Senior rating of student
    senior_rating_student INTEGER CHECK (senior_rating_student >= 1 AND senior_rating_student <= 5),
    senior_review_student TEXT CHECK (LENGTH(senior_review_student) <= 1000),
    senior_would_recommend BOOLEAN,
    senior_rated_at TIMESTAMP WITH TIME ZONE,
    
    -- Overall session quality
    session_quality_rating INTEGER CHECK (session_quality_rating >= 1 AND session_quality_rating <= 5),
    service_met_expectations BOOLEAN,
    
    -- Administrative flags
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    flagged_by UUID REFERENCES users(user_id),
    flagged_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Session photos and documentation
CREATE TABLE session_photos (
    photo_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(user_id),
    
    photo_url TEXT NOT NULL,
    photo_type VARCHAR(20) NOT NULL CHECK (photo_type IN ('check_in', 'check_out', 'during_session', 'completion', 'issue')),
    caption TEXT CHECK (LENGTH(caption) <= 500),
    
    -- Location where photo was taken
    location_id UUID REFERENCES gps_locations(location_id),
    taken_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- File information
    file_size INTEGER CHECK (file_size > 0),
    mime_type VARCHAR(100),
    original_filename VARCHAR(255),
    
    -- Content verification
    content_verified BOOLEAN DEFAULT FALSE,
    is_sensitive BOOLEAN DEFAULT FALSE, -- Flags photos that might contain sensitive info
    
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SESSION ALERTS AND MONITORING
-- =====================================================

-- Session alerts for various safety and operational concerns
CREATE TABLE session_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    triggered_by UUID REFERENCES users(user_id), -- User who triggered alert, if any
    
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'overtime', 'gps_drift', 'no_checkin', 'no_checkout', 'emergency', 
        'inactivity', 'late_arrival', 'location_mismatch', 'safety_concern'
    )),
    severity alert_severity NOT NULL,
    
    alert_title VARCHAR(200) NOT NULL,
    alert_message TEXT NOT NULL,
    alert_data JSONB DEFAULT '{}'::jsonb, -- Additional structured data
    
    -- Resolution tracking
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id),
    resolution_notes TEXT,
    resolution_action_taken VARCHAR(100),
    
    -- Escalation
    is_escalated BOOLEAN DEFAULT FALSE,
    escalated_to UUID REFERENCES admin_profiles(user_id),
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalation_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SESSION TIMELINE AND AUDIT TRAIL
-- =====================================================

-- Comprehensive audit trail for all session activities
CREATE TABLE session_timeline (
    timeline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    
    event_type VARCHAR(50) NOT NULL, -- created, scheduled, started, paused, resumed, completed, etc.
    event_description TEXT NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb, -- Structured event data
    
    -- User who triggered the event
    triggered_by UUID REFERENCES users(user_id),
    user_role VARCHAR(20), -- student, senior, admin, system
    
    -- Location where event occurred
    location_id UUID REFERENCES gps_locations(location_id),
    
    -- System context
    ip_address INET,
    user_agent TEXT,
    device_info JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SESSION CANCELLATIONS
-- =====================================================

-- Session cancellation tracking with detailed reasons
CREATE TABLE session_cancellations (
    cancellation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    cancelled_by UUID NOT NULL REFERENCES users(user_id),
    
    -- Cancellation details
    cancellation_reason VARCHAR(100) NOT NULL,
    detailed_reason TEXT CHECK (LENGTH(detailed_reason) <= 1000),
    is_emergency_cancellation BOOLEAN DEFAULT FALSE,
    advance_notice_hours DECIMAL(6, 2), -- How much notice was given
    
    -- Financial implications
    refund_required BOOLEAN DEFAULT FALSE,
    refund_amount DECIMAL(10, 2) CHECK (refund_amount >= 0),
    penalty_applied BOOLEAN DEFAULT FALSE,
    penalty_amount DECIMAL(10, 2) CHECK (penalty_amount >= 0),
    
    -- Rescheduling
    reschedule_requested BOOLEAN DEFAULT FALSE,
    new_session_id UUID REFERENCES sessions(session_id),
    
    cancelled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES admin_profiles(user_id)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- GPS locations indexes
CREATE INDEX idx_gps_locations_point ON gps_locations USING GIST(location_point);
CREATE INDEX idx_gps_locations_recorded_at ON gps_locations(recorded_at);
CREATE INDEX idx_gps_locations_city_state ON gps_locations(city, state_id);

-- Sessions indexes
CREATE INDEX idx_sessions_student ON sessions(student_id);
CREATE INDEX idx_sessions_senior ON sessions(senior_id);
CREATE INDEX idx_sessions_service_type ON sessions(service_type_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_scheduled_start ON sessions(scheduled_start_time);
CREATE INDEX idx_sessions_location ON sessions(location_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_active ON sessions(status) WHERE status IN ('scheduled', 'checked_in', 'in_progress');

-- Session requests indexes
CREATE INDEX idx_session_requests_student ON session_requests(student_id);
CREATE INDEX idx_session_requests_senior ON session_requests(senior_id);
CREATE INDEX idx_session_requests_status ON session_requests(status);
CREATE INDEX idx_session_requests_expires_at ON session_requests(expires_at);
CREATE INDEX idx_session_requests_pending ON session_requests(status) WHERE status = 'pending';

-- Session tracking indexes
CREATE INDEX idx_session_checkins_session ON session_checkins(session_id);
CREATE INDEX idx_session_checkins_user ON session_checkins(user_id);
CREATE INDEX idx_session_checkins_type ON session_checkins(checkin_type);
CREATE INDEX idx_session_checkins_time ON session_checkins(checkin_time);

CREATE INDEX idx_session_gps_tracking_session ON session_gps_tracking(session_id);
CREATE INDEX idx_session_gps_tracking_user ON session_gps_tracking(user_id);
CREATE INDEX idx_session_gps_tracking_recorded_at ON session_gps_tracking(recorded_at);

-- Ratings and feedback indexes
CREATE INDEX idx_session_ratings_session ON session_ratings(session_id);
CREATE INDEX idx_session_ratings_flagged ON session_ratings(is_flagged) WHERE is_flagged = TRUE;

-- Photos indexes
CREATE INDEX idx_session_photos_session ON session_photos(session_id);
CREATE INDEX idx_session_photos_uploaded_by ON session_photos(uploaded_by);
CREATE INDEX idx_session_photos_type ON session_photos(photo_type);

-- Alerts indexes
CREATE INDEX idx_session_alerts_session ON session_alerts(session_id);
CREATE INDEX idx_session_alerts_type_severity ON session_alerts(alert_type, severity);
CREATE INDEX idx_session_alerts_unresolved ON session_alerts(is_resolved) WHERE is_resolved = FALSE;
CREATE INDEX idx_session_alerts_escalated ON session_alerts(is_escalated) WHERE is_escalated = TRUE;

-- Timeline indexes
CREATE INDEX idx_session_timeline_session ON session_timeline(session_id);
CREATE INDEX idx_session_timeline_event_type ON session_timeline(event_type);
CREATE INDEX idx_session_timeline_created_at ON session_timeline(created_at);

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Auto-generate session numbers
CREATE OR REPLACE FUNCTION generate_session_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.session_number := 'SES-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                         LPAD(NEXTVAL('session_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for session numbers
CREATE SEQUENCE session_number_seq START 1;

-- Trigger to auto-generate session numbers
CREATE TRIGGER generate_session_number_trigger
    BEFORE INSERT ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION generate_session_number();

-- Function to automatically populate GPS location point from lat/lng
CREATE OR REPLACE FUNCTION update_location_point()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location_point := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update location point
CREATE TRIGGER update_gps_location_point
    BEFORE INSERT OR UPDATE ON gps_locations
    FOR EACH ROW
    EXECUTE FUNCTION update_location_point();

-- Function to auto-expire old session requests
CREATE OR REPLACE FUNCTION expire_old_session_requests()
RETURNS void AS $$
BEGIN
    UPDATE session_requests 
    SET status = 'expired' 
    WHERE status = 'pending' 
    AND expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to create timeline entry for session events
CREATE OR REPLACE FUNCTION create_session_timeline_entry(
    p_session_id UUID,
    p_event_type VARCHAR,
    p_event_description TEXT,
    p_triggered_by UUID DEFAULT NULL,
    p_event_data JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
    timeline_id UUID;
BEGIN
    INSERT INTO session_timeline (
        session_id, event_type, event_description, 
        triggered_by, event_data
    ) VALUES (
        p_session_id, p_event_type, p_event_description,
        p_triggered_by, p_event_data
    ) RETURNING timeline_id INTO timeline_id;
    
    RETURN timeline_id;
END;
$$ LANGUAGE plpgsql;

-- Function to validate GPS distance
CREATE OR REPLACE FUNCTION calculate_gps_distance_meters(
    lat1 DECIMAL, lon1 DECIMAL, 
    lat2 DECIMAL, lon2 DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_SetSRID(ST_MakePoint(lon1, lat1), 4326),
        ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically create timeline entries for major session events
CREATE OR REPLACE FUNCTION auto_create_timeline_entry()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM create_session_timeline_entry(
            NEW.session_id,
            'session_created',
            'Session was created',
            NULL, -- System event
            json_build_object('service_type_id', NEW.service_type_id, 'status', NEW.status)::jsonb
        );
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status != NEW.status THEN
            PERFORM create_session_timeline_entry(
                NEW.session_id,
                'status_changed',
                'Session status changed from ' || OLD.status || ' to ' || NEW.status,
                NULL,
                json_build_object('old_status', OLD.status, 'new_status', NEW.status)::jsonb
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto timeline creation
CREATE TRIGGER auto_session_timeline
    AFTER INSERT OR UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION auto_create_timeline_entry();

-- Add updated_at triggers
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();