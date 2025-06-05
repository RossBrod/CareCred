-- CareCred Database Complete Setup Script
-- Run this file to create the entire database schema

-- This script should be run in the following order:
-- 1. Create database (manually if needed)
-- 2. Connect to database
-- 3. Run this script

\echo 'Starting CareCred Database Setup...'

-- Set client encoding and timezone
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

\echo 'Step 1: Creating database types and extensions...'
\i 01_create_database.sql

\echo 'Step 2: Creating user tables...'
\i 02_create_users_tables.sql

\echo 'Step 3: Creating session tables...'
\i 03_create_sessions_tables.sql

\echo 'Step 4: Creating credit tables...'
\i 04_create_credits_tables.sql

\echo 'Step 5: Creating blockchain tables...'
\i 05_create_blockchain_tables.sql

\echo 'Step 6: Creating messaging tables...'
\i 06_create_messaging_tables.sql

\echo 'Step 7: Creating indexes and constraints...'
\i 07_create_indexes_constraints.sql

\echo 'Step 8: Creating sample data (optional)...'
-- Uncomment the line below if you want to load sample data
-- \i 08_sample_data.sql

-- Verify installation
\echo 'Verifying database setup...'

SELECT 'Database setup verification:' as status;

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

SELECT 'Total tables created: ' || count(*) as result
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

SELECT 'Total indexes created: ' || count(*) as result
FROM pg_indexes 
WHERE schemaname = 'public';

SELECT 'Total custom types created: ' || count(*) as result
FROM pg_type 
WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
AND typtype = 'e';

\echo 'CareCred Database Setup Complete!'
\echo 'You can now connect your application to this database.'