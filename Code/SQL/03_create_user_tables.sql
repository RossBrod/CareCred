-- CareCred User Tables - Properly Normalized
-- Follows 3NF principles with separate tables for each user type

-- =====================================================
-- CORE USER TABLES (NORMALIZED)
-- =====================================================

-- Base users table - contains only common fields
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    profile_photo_url TEXT,
    user_type user_type NOT NULL,
    status user_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Calculated fields (updated by triggers)
    total_sessions_count INTEGER DEFAULT 0 CHECK (total_sessions_count >= 0),
    average_rating DECIMAL(3,2) DEFAULT 0.0 CHECK (average_rating >= 0.0 AND average_rating <= 5.0),
    total_reviews_count INTEGER DEFAULT 0 CHECK (total_reviews_count >= 0)
);

-- Student profiles - only student-specific data
CREATE TABLE student_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    university_id UUID NOT NULL REFERENCES universities(university_id),
    major_id UUID NOT NULL REFERENCES academic_majors(major_id),
    student_id VARCHAR(50) NOT NULL,
    graduation_year INTEGER NOT NULL CHECK (graduation_year >= 2020 AND graduation_year <= 2035),
    gpa DECIMAL(3,2) CHECK (gpa >= 0.0 AND gpa <= 4.0),
    bio TEXT CHECK (LENGTH(bio) <= 1000),
    has_transportation BOOLEAN DEFAULT FALSE,
    max_travel_distance_miles DECIMAL(5,2) DEFAULT 5.0 CHECK (max_travel_distance_miles >= 0.0 AND max_travel_distance_miles <= 100.0),
    
    -- Academic verification
    enrollment_verified BOOLEAN DEFAULT FALSE,
    enrollment_verified_at TIMESTAMP WITH TIME ZONE,
    academic_standing VARCHAR(20) DEFAULT 'good', -- good, probation, suspension
    
    -- Availability and preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferred_session_duration_hours DECIMAL(3,1) DEFAULT 2.0,
    
    -- Performance metrics (calculated)
    total_credits_earned DECIMAL(12,2) DEFAULT 0.0 CHECK (total_credits_earned >= 0.0),
    total_hours_completed DECIMAL(10,2) DEFAULT 0.0 CHECK (total_hours_completed >= 0.0),
    active_sessions_count INTEGER DEFAULT 0 CHECK (active_sessions_count >= 0),
    completion_rate DECIMAL(5,2) DEFAULT 0.0 CHECK (completion_rate >= 0.0 AND completion_rate <= 100.0),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(university_id, student_id) -- Prevent duplicate student IDs per university
);

-- Senior profiles - only senior-specific data
CREATE TABLE senior_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    age INTEGER NOT NULL CHECK (age >= 55 AND age <= 120),
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_id INTEGER NOT NULL REFERENCES states(state_id),
    zip_code VARCHAR(10) NOT NULL,
    
    -- Location for matching (PostGIS point)
    location_point GEOMETRY(POINT, 4326), -- WGS84 coordinate system
    
    -- Emergency contact (normalized)
    emergency_contact_id UUID, -- Will reference emergency_contacts table
    
    -- Preferences and notes
    mobility_notes TEXT CHECK (LENGTH(mobility_notes) <= 1000),
    medical_notes TEXT CHECK (LENGTH(medical_notes) <= 1000),
    special_instructions TEXT CHECK (LENGTH(special_instructions) <= 1000),
    preferred_student_gender VARCHAR(20), -- any, male, female, non_binary
    
    -- Safety and verification
    background_check_completed BOOLEAN DEFAULT FALSE,
    background_check_date DATE,
    identity_verified BOOLEAN DEFAULT FALSE,
    identity_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Performance metrics (calculated)
    total_sessions_requested INTEGER DEFAULT 0 CHECK (total_sessions_requested >= 0),
    total_hours_received DECIMAL(10,2) DEFAULT 0.0 CHECK (total_hours_received >= 0.0),
    active_sessions_count INTEGER DEFAULT 0 CHECK (active_sessions_count >= 0),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Admin profiles - only admin-specific data
CREATE TABLE admin_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    admin_role admin_role NOT NULL,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(100),
    hire_date DATE DEFAULT CURRENT_DATE,
    supervisor_id UUID REFERENCES users(user_id), -- Self-referencing for reporting structure
    
    -- Access and permissions
    access_level INTEGER DEFAULT 1 CHECK (access_level >= 1 AND access_level <= 10),
    can_approve_seniors BOOLEAN DEFAULT FALSE,
    can_manage_credits BOOLEAN DEFAULT FALSE,
    can_access_reports BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    
    -- Activity tracking
    last_action_timestamp TIMESTAMP WITH TIME ZONE,
    total_actions_count INTEGER DEFAULT 0 CHECK (total_actions_count >= 0),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- RELATED USER TABLES
-- =====================================================

-- Emergency contacts (normalized from senior profiles)
CREATE TABLE emergency_contacts (
    contact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    senior_id UUID NOT NULL REFERENCES senior_profiles(user_id) ON DELETE CASCADE,
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50), -- daughter, son, neighbor, friend, etc.
    phone_primary VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    email VARCHAR(255),
    address VARCHAR(200),
    city VARCHAR(100),
    state_id INTEGER REFERENCES states(state_id),
    zip_code VARCHAR(10),
    is_primary BOOLEAN DEFAULT FALSE,
    can_authorize_sessions BOOLEAN DEFAULT FALSE,
    preferred_contact_method VARCHAR(20) DEFAULT 'phone', -- phone, email, sms
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Student skills (many-to-many relationship)
CREATE TABLE student_skills (
    user_id UUID NOT NULL REFERENCES student_profiles(user_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) DEFAULT 'basic', -- basic, intermediate, advanced, expert
    years_experience INTEGER DEFAULT 0 CHECK (years_experience >= 0),
    is_certified BOOLEAN DEFAULT FALSE,
    certification_details TEXT,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, skill_id)
);

-- Senior help needs (many-to-many relationship)
CREATE TABLE senior_help_needs (
    user_id UUID NOT NULL REFERENCES senior_profiles(user_id) ON DELETE CASCADE,
    service_type_id UUID NOT NULL REFERENCES service_types(service_type_id) ON DELETE CASCADE,
    priority_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    frequency VARCHAR(20) DEFAULT 'as_needed', -- daily, weekly, monthly, as_needed
    preferred_time_of_day VARCHAR(20), -- morning, afternoon, evening, flexible
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, service_type_id)
);

-- User availability schedules (normalized from JSON)
CREATE TABLE user_availability (
    availability_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_time_range CHECK (end_time > start_time),
    CONSTRAINT check_date_range CHECK (end_date IS NULL OR end_date > effective_date)
);

-- User authentication tokens
CREATE TABLE user_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('access', 'refresh', 'verification', 'reset')),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    device_fingerprint VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    UNIQUE(token_hash)
);

-- User devices for push notifications
CREATE TABLE user_devices (
    device_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_token VARCHAR(255) NOT NULL,
    device_type VARCHAR(20) CHECK (device_type IN ('ios', 'android', 'web')),
    device_name VARCHAR(100), -- "iPhone 12", "Samsung Galaxy", etc.
    app_version VARCHAR(20),
    os_version VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(device_token)
);

-- User verification documents
CREATE TABLE user_verification_documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- drivers_license, passport, student_id, etc.
    document_url TEXT NOT NULL,
    file_size INTEGER CHECK (file_size > 0),
    mime_type VARCHAR(100),
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES admin_profiles(user_id),
    rejection_reason TEXT,
    expiry_date DATE -- For documents that expire
);

-- User preferences and settings
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Notification preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    
    -- Privacy settings
    profile_visibility VARCHAR(20) DEFAULT 'public', -- public, limited, private
    share_location BOOLEAN DEFAULT TRUE,
    share_contact_info BOOLEAN DEFAULT FALSE,
    
    -- Communication preferences
    preferred_contact_method VARCHAR(20) DEFAULT 'app', -- app, email, phone, sms
    language_preference VARCHAR(10) DEFAULT 'en',
    
    -- Scheduling preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    min_notice_hours INTEGER DEFAULT 24 CHECK (min_notice_hours >= 1),
    auto_accept_sessions BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type_status ON users(user_type, status);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);

-- Student profiles indexes
CREATE INDEX idx_student_profiles_university ON student_profiles(university_id);
CREATE INDEX idx_student_profiles_major ON student_profiles(major_id);
CREATE INDEX idx_student_profiles_graduation_year ON student_profiles(graduation_year);
CREATE INDEX idx_student_profiles_transportation ON student_profiles(has_transportation);
CREATE INDEX idx_student_profiles_distance ON student_profiles(max_travel_distance_miles);
CREATE INDEX idx_student_profiles_verified ON student_profiles(enrollment_verified) WHERE enrollment_verified = TRUE;

-- Senior profiles indexes
CREATE INDEX idx_senior_profiles_state ON senior_profiles(state_id);
CREATE INDEX idx_senior_profiles_city ON senior_profiles(city);
CREATE INDEX idx_senior_profiles_zip ON senior_profiles(zip_code);
CREATE INDEX idx_senior_profiles_age ON senior_profiles(age);
CREATE INDEX idx_senior_profiles_verified ON senior_profiles(identity_verified) WHERE identity_verified = TRUE;
-- PostGIS spatial index
CREATE INDEX idx_senior_profiles_location ON senior_profiles USING GIST(location_point);

-- Admin profiles indexes
CREATE INDEX idx_admin_profiles_role ON admin_profiles(admin_role);
CREATE INDEX idx_admin_profiles_department ON admin_profiles(department);
CREATE INDEX idx_admin_profiles_supervisor ON admin_profiles(supervisor_id);

-- Relationship table indexes
CREATE INDEX idx_student_skills_skill ON student_skills(skill_id);
CREATE INDEX idx_student_skills_proficiency ON student_skills(proficiency_level);
CREATE INDEX idx_senior_help_needs_service_type ON senior_help_needs(service_type_id);
CREATE INDEX idx_senior_help_needs_active ON senior_help_needs(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_user_availability_user ON user_availability(user_id);
CREATE INDEX idx_user_availability_day ON user_availability(day_of_week);
CREATE INDEX idx_user_availability_active ON user_availability(is_active) WHERE is_active = TRUE;

-- Emergency contacts indexes
CREATE INDEX idx_emergency_contacts_senior ON emergency_contacts(senior_id);
CREATE INDEX idx_emergency_contacts_primary ON emergency_contacts(is_primary) WHERE is_primary = TRUE;

-- Tokens and devices indexes
CREATE INDEX idx_user_tokens_user ON user_tokens(user_id);
CREATE INDEX idx_user_tokens_type ON user_tokens(token_type);
CREATE INDEX idx_user_tokens_expires ON user_tokens(expires_at);
CREATE INDEX idx_user_tokens_active ON user_tokens(user_id, token_type) WHERE revoked = FALSE;
CREATE INDEX idx_user_devices_user ON user_devices(user_id);
CREATE INDEX idx_user_devices_active ON user_devices(is_active) WHERE is_active = TRUE;

-- =====================================================
-- CONSTRAINTS AND BUSINESS RULES
-- =====================================================

-- Ensure only one primary emergency contact per senior
CREATE UNIQUE INDEX idx_emergency_contacts_one_primary 
ON emergency_contacts(senior_id) 
WHERE is_primary = TRUE;

-- Ensure user_type matches profile table
CREATE OR REPLACE FUNCTION validate_user_profile_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if user type matches the profile table being inserted into
    IF TG_TABLE_NAME = 'student_profiles' THEN
        IF (SELECT user_type FROM users WHERE user_id = NEW.user_id) != 'student' THEN
            RAISE EXCEPTION 'User type must be student for student_profiles';
        END IF;
    ELSIF TG_TABLE_NAME = 'senior_profiles' THEN
        IF (SELECT user_type FROM users WHERE user_id = NEW.user_id) != 'senior' THEN
            RAISE EXCEPTION 'User type must be senior for senior_profiles';
        END IF;
    ELSIF TG_TABLE_NAME = 'admin_profiles' THEN
        IF (SELECT user_type FROM users WHERE user_id = NEW.user_id) != 'admin' THEN
            RAISE EXCEPTION 'User type must be admin for admin_profiles';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers to enforce user type consistency
CREATE TRIGGER validate_student_profile_user_type
    BEFORE INSERT OR UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION validate_user_profile_consistency();

CREATE TRIGGER validate_senior_profile_user_type
    BEFORE INSERT OR UPDATE ON senior_profiles
    FOR EACH ROW EXECUTE FUNCTION validate_user_profile_consistency();

CREATE TRIGGER validate_admin_profile_user_type
    BEFORE INSERT OR UPDATE ON admin_profiles
    FOR EACH ROW EXECUTE FUNCTION validate_user_profile_consistency();

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Update timestamp trigger function (shared)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_profiles_updated_at BEFORE UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_senior_profiles_updated_at BEFORE UPDATE ON senior_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_profiles_updated_at BEFORE UPDATE ON admin_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to check if user profile exists for user type
CREATE OR REPLACE FUNCTION user_profile_exists(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_type_val user_type;
    profile_exists BOOLEAN := FALSE;
BEGIN
    SELECT user_type INTO user_type_val FROM users WHERE user_id = p_user_id;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    CASE user_type_val
        WHEN 'student' THEN
            SELECT EXISTS(SELECT 1 FROM student_profiles WHERE user_id = p_user_id) INTO profile_exists;
        WHEN 'senior' THEN
            SELECT EXISTS(SELECT 1 FROM senior_profiles WHERE user_id = p_user_id) INTO profile_exists;
        WHEN 'admin' THEN
            SELECT EXISTS(SELECT 1 FROM admin_profiles WHERE user_id = p_user_id) INTO profile_exists;
    END CASE;
    
    RETURN profile_exists;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's full name
CREATE OR REPLACE FUNCTION get_user_full_name(p_user_id UUID)
RETURNS TEXT AS $$
DECLARE
    full_name TEXT;
BEGIN
    SELECT CONCAT(first_name, ' ', last_name) INTO full_name
    FROM users
    WHERE user_id = p_user_id;
    
    RETURN full_name;
END;
$$ LANGUAGE plpgsql;