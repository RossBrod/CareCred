-- CareCred Database Schema - PostgreSQL
-- Database Creation and Setup

-- Create database (run this separately if needed)
-- CREATE DATABASE carecred_db;

-- Connect to the database
-- \c carecred_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_type AS ENUM ('student', 'senior', 'admin');
CREATE TYPE user_status AS ENUM ('pending', 'approved', 'rejected', 'suspended');
CREATE TYPE admin_role AS ENUM ('super_admin', 'moderator', 'support', 'financial');

CREATE TYPE session_status AS ENUM (
    'requested', 'approved', 'scheduled', 'checked_in', 
    'in_progress', 'completed', 'cancelled', 'disputed'
);

CREATE TYPE session_type AS ENUM (
    'grocery_shopping', 'technology_help', 'transportation', 
    'companionship', 'light_housekeeping', 'meal_preparation', 
    'pet_care', 'home_maintenance', 'medical_appointment'
);

CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TYPE transaction_status AS ENUM ('pending', 'confirmed', 'failed', 'rejected');
CREATE TYPE signature_status AS ENUM ('pending', 'collected', 'expired');
CREATE TYPE task_type AS ENUM (
    'companionship', 'transportation', 'technology_help', 
    'household_tasks', 'medication_reminder', 'other'
);

CREATE TYPE credit_transaction_type AS ENUM ('earned', 'disbursed', 'adjusted', 'refunded');
CREATE TYPE credit_transaction_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE disbursement_type AS ENUM ('tuition', 'housing', 'books', 'meal_plan', 'mixed');
CREATE TYPE payment_method AS ENUM ('ach', 'wire', 'check', 'direct_api');

-- Set timezone
SET timezone = 'UTC';