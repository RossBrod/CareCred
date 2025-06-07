-- CareCred Database Schema - PostgreSQL (Normalized)
-- Properly Normalized Database Following 3NF Principles
-- Schema carries meaning through its structure and relationships

-- Create database (run this separately if needed)
-- CREATE DATABASE carecred_db;

-- Connect to the database
-- \c carecred_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis"; -- For geographic calculations

-- Create custom types
CREATE TYPE user_type AS ENUM ('student', 'senior', 'admin');
CREATE TYPE user_status AS ENUM ('pending', 'active', 'suspended', 'deactivated');
CREATE TYPE admin_role AS ENUM ('super_admin', 'platform_admin', 'customer_service', 'financial_admin');

CREATE TYPE session_status AS ENUM (
    'requested', 'approved', 'scheduled', 'checked_in', 
    'in_progress', 'completed', 'cancelled', 'disputed'
);

CREATE TYPE service_category AS ENUM (
    'household', 'transportation', 'technology', 'companionship', 
    'health_support', 'errands', 'maintenance'
);

CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE transaction_status AS ENUM ('pending', 'confirmed', 'failed', 'rejected');
CREATE TYPE signature_status AS ENUM ('pending', 'collected', 'expired');

CREATE TYPE credit_transaction_type AS ENUM ('earned', 'disbursed', 'adjusted', 'refunded');
CREATE TYPE credit_transaction_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE disbursement_category AS ENUM ('tuition', 'housing', 'books', 'meal_plan', 'transportation', 'other');
CREATE TYPE payment_method AS ENUM ('ach', 'wire', 'check', 'direct_api');

CREATE TYPE message_type AS ENUM ('text', 'image', 'document', 'system', 'session_update', 'emergency');
CREATE TYPE message_status AS ENUM ('sent', 'delivered', 'read', 'failed');
CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent', 'emergency');
CREATE TYPE notification_channel AS ENUM ('email', 'sms', 'push', 'in_app');

-- Set timezone
SET timezone = 'UTC';