-- CareCred Reference Tables - Lookup/Master Data
-- These tables define the core entities that other tables reference

-- =====================================================
-- GEOGRAPHIC AND INSTITUTIONAL REFERENCE DATA
-- =====================================================

-- States/Provinces lookup table
CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    state_code VARCHAR(3) NOT NULL UNIQUE, -- US: CA, TX, etc. Canada: ON, BC
    state_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(3) NOT NULL DEFAULT 'USA',
    timezone_default VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Universities and educational institutions
CREATE TABLE universities (
    university_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    university_name VARCHAR(200) NOT NULL,
    university_code VARCHAR(20) UNIQUE, -- UCSD, UCLA, etc.
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_id INTEGER NOT NULL REFERENCES states(state_id),
    zip_code VARCHAR(10) NOT NULL,
    website_url TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    
    -- Integration details for credit disbursement
    accepts_direct_disbursement BOOLEAN DEFAULT FALSE,
    api_endpoint TEXT,
    integration_type VARCHAR(20) CHECK (integration_type IN ('api', 'file_transfer', 'manual')),
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    accreditation_info TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Academic majors/fields of study
CREATE TABLE academic_majors (
    major_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    major_name VARCHAR(200) NOT NULL UNIQUE,
    major_category VARCHAR(100), -- STEM, Liberal Arts, Business, etc.
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills taxonomy for matching students to seniors
CREATE TABLE skills (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50), -- technology, household, healthcare, etc.
    description TEXT,
    requires_certification BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SERVICE AND SESSION REFERENCE DATA
-- =====================================================

-- Service types that students can provide
CREATE TABLE service_types (
    service_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL UNIQUE,
    service_category service_category NOT NULL,
    description TEXT,
    estimated_duration_hours DECIMAL(4,2) DEFAULT 1.0,
    base_hourly_rate DECIMAL(6,2) DEFAULT 15.00,
    requires_transportation BOOLEAN DEFAULT FALSE,
    requires_background_check BOOLEAN DEFAULT TRUE,
    requires_special_skills BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills required for specific service types (many-to-many)
CREATE TABLE service_type_skills (
    service_type_id UUID NOT NULL REFERENCES service_types(service_type_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT TRUE, -- vs nice-to-have
    proficiency_level VARCHAR(20) DEFAULT 'basic', -- basic, intermediate, advanced
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (service_type_id, skill_id)
);

-- =====================================================
-- FINANCIAL REFERENCE DATA
-- =====================================================

-- Credit rate schedules (rates can change over time)
CREATE TABLE credit_rate_schedules (
    rate_schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_type_id UUID NOT NULL REFERENCES service_types(service_type_id),
    hourly_rate DECIMAL(6,2) NOT NULL CHECK (hourly_rate > 0),
    effective_date DATE NOT NULL,
    end_date DATE,
    created_by UUID, -- Will reference users(user_id) after users table is created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_rate_dates CHECK (end_date IS NULL OR end_date > effective_date)
);

-- Government funding sources
CREATE TABLE funding_sources (
    funding_source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50), -- federal_grant, state_grant, private_foundation, etc.
    contact_name VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    funding_cycle VARCHAR(50), -- monthly, quarterly, annual
    total_annual_budget DECIMAL(15,2),
    remaining_budget DECIMAL(15,2),
    budget_year INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR REFERENCE TABLES
-- =====================================================

-- States indexes
CREATE INDEX idx_states_country_code ON states(country_code);
CREATE INDEX idx_states_active ON states(is_active) WHERE is_active = TRUE;

-- Universities indexes
CREATE INDEX idx_universities_state ON universities(state_id);
CREATE INDEX idx_universities_verified ON universities(is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_universities_name_search ON universities USING gin(to_tsvector('english', university_name));

-- Skills indexes
CREATE INDEX idx_skills_category ON skills(skill_category);
CREATE INDEX idx_skills_active ON skills(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_skills_name_search ON skills USING gin(to_tsvector('english', skill_name));

-- Service types indexes
CREATE INDEX idx_service_types_category ON service_types(service_category);
CREATE INDEX idx_service_types_active ON service_types(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_service_types_transportation ON service_types(requires_transportation);

-- Rate schedules indexes
CREATE INDEX idx_rate_schedules_service_type ON credit_rate_schedules(service_type_id);
CREATE INDEX idx_rate_schedules_effective_date ON credit_rate_schedules(effective_date);
CREATE INDEX idx_rate_schedules_current ON credit_rate_schedules(service_type_id, effective_date) 
    WHERE end_date IS NULL OR end_date > CURRENT_DATE;

-- =====================================================
-- FUNCTIONS FOR REFERENCE DATA
-- =====================================================

-- Function to get current rate for a service type
CREATE OR REPLACE FUNCTION get_current_hourly_rate(p_service_type_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    current_rate DECIMAL(6,2);
BEGIN
    SELECT hourly_rate INTO current_rate
    FROM credit_rate_schedules
    WHERE service_type_id = p_service_type_id
    AND effective_date <= CURRENT_DATE
    AND (end_date IS NULL OR end_date > CURRENT_DATE)
    ORDER BY effective_date DESC
    LIMIT 1;
    
    IF current_rate IS NULL THEN
        -- Fallback to service type base rate
        SELECT base_hourly_rate INTO current_rate
        FROM service_types
        WHERE service_type_id = p_service_type_id;
    END IF;
    
    RETURN COALESCE(current_rate, 15.00);
END;
$$ LANGUAGE plpgsql;

-- Function to validate university exists and is verified
CREATE OR REPLACE FUNCTION is_university_verified(p_university_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    is_verified BOOLEAN;
BEGIN
    SELECT universities.is_verified INTO is_verified
    FROM universities
    WHERE university_id = p_university_id;
    
    RETURN COALESCE(is_verified, FALSE);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INSERT REFERENCE DATA
-- =====================================================

-- Insert US states
INSERT INTO states (state_code, state_name, country_code, timezone_default) VALUES
('CA', 'California', 'USA', 'America/Los_Angeles'),
('TX', 'Texas', 'USA', 'America/Chicago'),
('NY', 'New York', 'USA', 'America/New_York'),
('FL', 'Florida', 'USA', 'America/New_York'),
('IL', 'Illinois', 'USA', 'America/Chicago'),
('OH', 'Ohio', 'USA', 'America/New_York'),
('PA', 'Pennsylvania', 'USA', 'America/New_York'),
('MI', 'Michigan', 'USA', 'America/New_York'),
('GA', 'Georgia', 'USA', 'America/New_York'),
('NC', 'North Carolina', 'USA', 'America/New_York'),
('NJ', 'New Jersey', 'USA', 'America/New_York'),
('VA', 'Virginia', 'USA', 'America/New_York'),
('WA', 'Washington', 'USA', 'America/Los_Angeles'),
('AZ', 'Arizona', 'USA', 'America/Phoenix'),
('MA', 'Massachusetts', 'USA', 'America/New_York'),
('TN', 'Tennessee', 'USA', 'America/Chicago'),
('IN', 'Indiana', 'USA', 'America/New_York'),
('MO', 'Missouri', 'USA', 'America/Chicago'),
('MD', 'Maryland', 'USA', 'America/New_York'),
('WI', 'Wisconsin', 'USA', 'America/Chicago');

-- Insert major California universities
INSERT INTO universities (university_name, university_code, address, city, state_id, zip_code, website_url, is_verified) VALUES
('University of California, San Diego', 'UCSD', '9500 Gilman Dr', 'La Jolla', 1, '92093', 'https://ucsd.edu', TRUE),
('University of California, Los Angeles', 'UCLA', '405 Hilgard Ave', 'Los Angeles', 1, '90095', 'https://ucla.edu', TRUE),
('University of California, Berkeley', 'UCB', '110 Sproul Hall', 'Berkeley', 1, '94720', 'https://berkeley.edu', TRUE),
('Stanford University', 'STANFORD', '450 Serra Mall', 'Stanford', 1, '94305', 'https://stanford.edu', TRUE),
('California Institute of Technology', 'CALTECH', '1200 E California Blvd', 'Pasadena', 1, '91125', 'https://caltech.edu', TRUE),
('University of Southern California', 'USC', 'University Park Campus', 'Los Angeles', 1, '90089', 'https://usc.edu', TRUE),
('San Diego State University', 'SDSU', '5500 Campanile Dr', 'San Diego', 1, '92182', 'https://sdsu.edu', TRUE);

-- Insert academic majors
INSERT INTO academic_majors (major_name, major_category) VALUES
('Computer Science', 'STEM'),
('Bioengineering', 'STEM'),
('Psychology', 'Social Sciences'),
('Business Administration', 'Business'),
('Nursing', 'Health Sciences'),
('Education', 'Education'),
('Social Work', 'Social Sciences'),
('Communications', 'Liberal Arts'),
('Biology', 'STEM'),
('Chemistry', 'STEM'),
('Mathematics', 'STEM'),
('English Literature', 'Liberal Arts'),
('Economics', 'Social Sciences'),
('Political Science', 'Social Sciences'),
('Art History', 'Liberal Arts'),
('Music', 'Liberal Arts'),
('Mechanical Engineering', 'STEM'),
('Public Health', 'Health Sciences'),
('International Relations', 'Social Sciences'),
('Environmental Science', 'STEM');

-- Insert skills
INSERT INTO skills (skill_name, skill_category, requires_certification) VALUES
('Basic Computer Skills', 'technology', FALSE),
('Smartphone/Tablet Help', 'technology', FALSE),
('Video Calling Setup', 'technology', FALSE),
('Social Media Assistance', 'technology', FALSE),
('Light Housekeeping', 'household', FALSE),
('Meal Preparation', 'household', FALSE),
('Grocery Shopping', 'errands', FALSE),
('Transportation', 'transportation', TRUE), -- Requires valid driver's license
('Companionship', 'social', FALSE),
('Reading Assistance', 'health_support', FALSE),
('Medication Reminders', 'health_support', TRUE), -- May require training
('Pet Care', 'household', FALSE),
('Garden Maintenance', 'household', FALSE),
('Home Organization', 'household', FALSE),
('Appointment Scheduling', 'administrative', FALSE),
('Basic First Aid', 'health_support', TRUE),
('Spanish Language', 'communication', FALSE),
('Sign Language', 'communication', TRUE),
('Financial Organization', 'administrative', FALSE),
('Technology Troubleshooting', 'technology', FALSE);

-- Insert service types
INSERT INTO service_types (service_name, service_category, description, estimated_duration_hours, base_hourly_rate, requires_transportation, requires_special_skills) VALUES
('Grocery Shopping', 'errands', 'Assistance with grocery shopping and errands', 2.0, 15.00, TRUE, FALSE),
('Technology Help', 'technology', 'Help with computers, smartphones, and digital devices', 1.5, 18.00, FALSE, TRUE),
('Transportation Services', 'transportation', 'Safe transportation to appointments and errands', 2.0, 20.00, TRUE, TRUE),
('Companionship', 'companionship', 'Social interaction and emotional support', 3.0, 15.00, FALSE, FALSE),
('Light Housekeeping', 'household', 'Basic cleaning and household organization', 2.5, 16.00, FALSE, FALSE),
('Meal Preparation', 'household', 'Cooking and meal planning assistance', 2.0, 17.00, FALSE, FALSE),
('Pet Care', 'household', 'Pet walking, feeding, and basic care', 1.5, 14.00, FALSE, FALSE),
('Home Maintenance', 'maintenance', 'Basic home repairs and maintenance tasks', 3.0, 22.00, FALSE, TRUE),
('Medical Appointment Support', 'health_support', 'Accompaniment to medical appointments', 3.0, 18.00, TRUE, FALSE),
('Administrative Help', 'errands', 'Assistance with paperwork and organization', 2.0, 16.00, FALSE, FALSE);

-- Insert funding sources
INSERT INTO funding_sources (source_name, source_type, funding_cycle, total_annual_budget, budget_year, is_active) VALUES
('Federal Senior Care Grant Program', 'federal_grant', 'quarterly', 50000000.00, 2024, TRUE),
('California Community Care Initiative', 'state_grant', 'monthly', 12000000.00, 2024, TRUE),
('Smith Foundation Aging Support Fund', 'private_foundation', 'annual', 2500000.00, 2024, TRUE),
('AARP Community Connections Grant', 'nonprofit_grant', 'quarterly', 8000000.00, 2024, TRUE);

-- Add updated_at triggers
CREATE TRIGGER update_universities_updated_at BEFORE UPDATE ON universities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();