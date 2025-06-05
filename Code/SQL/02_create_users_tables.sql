-- CareCred Users Tables
-- Unified users table with role-specific columns

-- Main users table (base for all user types)
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
    background_check_status VARCHAR(50),
    rating DECIMAL(2,1) DEFAULT 0.0 CHECK (rating >= 0.0 AND rating <= 5.0),
    total_reviews INTEGER DEFAULT 0 CHECK (total_reviews >= 0),
    
    -- Student-specific fields
    university VARCHAR(100),
    student_id VARCHAR(50),
    major VARCHAR(100),
    graduation_year INTEGER CHECK (graduation_year >= 2020 AND graduation_year <= 2035),
    bio TEXT,
    skills JSONB DEFAULT '[]'::jsonb,
    availability_schedule JSONB DEFAULT '{}'::jsonb,
    has_transportation BOOLEAN DEFAULT FALSE,
    max_travel_distance DECIMAL(5,2) DEFAULT 0.0 CHECK (max_travel_distance >= 0.0 AND max_travel_distance <= 100.0),
    total_credits_earned DECIMAL(10,2) DEFAULT 0.0 CHECK (total_credits_earned >= 0.0),
    total_hours_completed DECIMAL(10,2) DEFAULT 0.0 CHECK (total_hours_completed >= 0.0),
    active_sessions_count INTEGER DEFAULT 0 CHECK (active_sessions_count >= 0),
    
    -- Senior-specific fields
    age INTEGER CHECK (age >= 55 AND age <= 120),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    help_needed JSONB DEFAULT '[]'::jsonb,
    mobility_notes TEXT,
    medical_notes TEXT,
    preferred_times JSONB DEFAULT '{}'::jsonb,
    total_sessions_completed INTEGER DEFAULT 0 CHECK (total_sessions_completed >= 0),
    total_hours_received DECIMAL(10,2) DEFAULT 0.0 CHECK (total_hours_received >= 0.0),
    
    -- Admin-specific fields
    admin_role admin_role,
    permissions JSONB DEFAULT '[]'::jsonb,
    department VARCHAR(100),
    employee_id VARCHAR(50),
    last_action_timestamp TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_student_fields CHECK (
        user_type != 'student' OR (
            university IS NOT NULL AND 
            student_id IS NOT NULL AND 
            major IS NOT NULL AND 
            graduation_year IS NOT NULL
        )
    ),
    CONSTRAINT check_senior_fields CHECK (
        user_type != 'senior' OR (
            age IS NOT NULL AND 
            address IS NOT NULL AND 
            city IS NOT NULL AND 
            state IS NOT NULL AND 
            zip_code IS NOT NULL AND 
            emergency_contact_name IS NOT NULL AND 
            emergency_contact_phone IS NOT NULL
        )
    ),
    CONSTRAINT check_admin_fields CHECK (
        user_type != 'admin' OR (
            admin_role IS NOT NULL AND 
            employee_id IS NOT NULL
        )
    )
);

-- JWT tokens and session management
CREATE TABLE user_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('access', 'refresh', 'verification', 'reset')),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    device_info JSONB,
    ip_address INET,
    
    UNIQUE(token_hash)
);

-- User verification documents
CREATE TABLE user_verification_documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_url TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    verification_status VARCHAR(20) DEFAULT 'pending',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(user_id),
    rejection_reason TEXT
);

-- User device registrations for push notifications
CREATE TABLE user_devices (
    device_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_token VARCHAR(255) NOT NULL,
    device_type VARCHAR(20) CHECK (device_type IN ('ios', 'android', 'web')),
    device_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(device_token)
);

-- User availability schedules (normalized)
CREATE TABLE user_availability (
    availability_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_time_range CHECK (end_time > start_time)
);

-- User preferences and settings
CREATE TABLE user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    preference_type VARCHAR(50) NOT NULL,
    preference_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, preference_type)
);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();