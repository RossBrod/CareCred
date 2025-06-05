# CareCred Database Schema

This directory contains the complete PostgreSQL database schema for the CareCred application - a platform connecting college students with senior citizens for service exchange and credit tracking.

## Overview

The database is designed to support:
- User management (students, seniors, administrators)
- Session scheduling and GPS tracking
- Credit calculation and disbursement
- Blockchain transaction logging
- Messaging and notifications
- Financial operations and reporting

## Database Setup

### Prerequisites
- PostgreSQL 13+ (recommended)
- Extensions: `uuid-ossp`, `pgcrypto`

### Installation

1. **Create Database:**
   ```sql
   CREATE DATABASE carecred_db;
   \c carecred_db;
   ```

2. **Run Setup Script:**
   ```bash
   psql -d carecred_db -f 00_setup_all.sql
   ```

   Or run individual files in order:
   ```bash
   psql -d carecred_db -f 01_create_database.sql
   psql -d carecred_db -f 02_create_users_tables.sql
   psql -d carecred_db -f 03_create_sessions_tables.sql
   psql -d carecred_db -f 04_create_credits_tables.sql
   psql -d carecred_db -f 05_create_blockchain_tables.sql
   psql -d carecred_db -f 06_create_messaging_tables.sql
   psql -d carecred_db -f 07_create_indexes_constraints.sql
   ```

## Schema Files

| File | Description |
|------|-------------|
| `00_setup_all.sql` | Master setup script that runs all components |
| `01_create_database.sql` | Database creation, extensions, and custom types |
| `02_create_users_tables.sql` | User management tables (students, seniors, admins) |
| `03_create_sessions_tables.sql` | Session tracking and GPS verification |
| `04_create_credits_tables.sql` | Credit accounts, transactions, and disbursements |
| `05_create_blockchain_tables.sql` | Blockchain logging and verification |
| `06_create_messaging_tables.sql` | Messaging, notifications, and alerts |
| `07_create_indexes_constraints.sql` | Performance indexes and constraints |

## Core Tables

### User Management
- **`users`** - Unified table for all user types with role-specific columns
- **`user_tokens`** - JWT token management and session tracking
- **`user_verification_documents`** - Identity verification uploads
- **`user_availability`** - User scheduling preferences
- **`notification_preferences`** - User notification settings

### Session Management
- **`sessions`** - Core session data with GPS and blockchain integration
- **`session_requests`** - Session request workflow
- **`gps_locations`** - GPS coordinate storage with privacy hashing
- **`session_alerts`** - Real-time session monitoring alerts
- **`session_gps_tracking`** - Continuous GPS tracking during sessions

### Financial Operations
- **`credit_accounts`** - Student credit balance tracking
- **`credit_transactions`** - Individual credit earning/spending records
- **`credit_disbursements`** - Payments to institutions
- **`government_payments`** - Government funding tracking
- **`payment_allocations`** - Distribution of government payments to students

### Blockchain Integration
- **`blockchain_session_logs`** - Immutable session records for blockchain
- **`blockchain_transactions`** - Solana transaction tracking
- **`signature_requests`** - Digital signature collection workflow
- **`verification_results`** - Blockchain verification outcomes

### Communication
- **`conversations`** - Message threads between users
- **`messages`** - Individual messages with encryption support
- **`notifications`** - System-generated notifications
- **`emergency_alerts`** - Emergency communication system

## Key Features

### Security & Privacy
- **Password hashing** using pgcrypto
- **PII hashing** for blockchain privacy
- **JWT token management** with expiration
- **Role-based access control** via permissions
- **Message encryption** support

### Performance Optimization
- **Comprehensive indexing** for common query patterns
- **Partial indexes** for frequently filtered data
- **Materialized views** for aggregated statistics
- **Automatic cleanup** functions for expired data

### Data Integrity
- **Check constraints** for data validation
- **Foreign key relationships** with proper cascading
- **Unique constraints** to prevent duplicates
- **Trigger functions** for automatic updates

### GPS & Location Services
- **Coordinate validation** within valid ranges
- **Distance calculation** functions
- **Geofencing validation** for check-ins
- **GPS accuracy tracking** for verification

### Blockchain Integration
- **Session hash generation** for immutable records
- **Digital signature validation** 
- **Transaction status tracking** with retry logic
- **Verification result logging**

## Custom Types

The schema defines several PostgreSQL enum types:

```sql
-- User types
user_type: 'student', 'senior', 'admin'
user_status: 'pending', 'approved', 'rejected', 'suspended'
admin_role: 'super_admin', 'moderator', 'support', 'financial'

-- Session types
session_status: 'requested', 'approved', 'scheduled', 'checked_in', 'in_progress', 'completed', 'cancelled', 'disputed'
session_type: 'grocery_shopping', 'technology_help', 'transportation', 'companionship', etc.

-- Financial types
credit_transaction_type: 'earned', 'disbursed', 'adjusted', 'refunded'
disbursement_type: 'tuition', 'housing', 'books', 'meal_plan', 'mixed'

-- Communication types
message_type: 'text', 'image', 'document', 'system', 'emergency'
notification_priority: 'low', 'normal', 'high', 'urgent', 'emergency'
```

## Key Functions

### Utility Functions
- `update_updated_at_column()` - Automatic timestamp updates
- `calculate_session_duration()` - Session duration calculation
- `validate_gps_distance()` - GPS proximity validation

### Credit Management
- `calculate_available_balance()` - Real-time balance calculation
- `update_account_balance()` - Account balance synchronization
- `validate_disbursement_split()` - Percentage validation

### Blockchain Functions
- `generate_session_hash()` - Unique session identification
- `is_session_ready_for_blockchain()` - Blockchain logging eligibility
- `create_blockchain_session_log()` - Blockchain record creation

### Messaging Functions
- `update_unread_counts()` - Message read status tracking
- `is_in_quiet_hours()` - Notification timing validation
- `create_system_message()` - Automated message generation

## Performance Considerations

### Indexing Strategy
- **Primary operations** are indexed for sub-second response
- **Composite indexes** for multi-column queries
- **Partial indexes** for frequently filtered subsets
- **Covering indexes** to avoid table lookups

### Query Optimization
- **Materialized views** for expensive aggregations
- **Function-based indexes** for computed columns
- **Constraint exclusion** for date-partitioned queries

### Maintenance
- **Automatic cleanup** of expired tokens and notifications
- **Statistics refresh** for query planner optimization
- **Index rebuild** recommendations for fragmented indexes

## Security Considerations

### Access Control
- **Role-based permissions** in application layer
- **Row-level security** can be added if needed
- **Audit trails** for sensitive operations

### Data Protection
- **Password hashing** using bcrypt-compatible functions
- **PII anonymization** for blockchain records
- **Secure token generation** with proper entropy

## Monitoring & Maintenance

### Regular Tasks
```sql
-- Clean up expired data
SELECT cleanup_expired_data();

-- Refresh statistics
SELECT refresh_materialized_views();

-- Monitor performance
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';
```

### Health Checks
- Monitor index usage via `pg_stat_user_indexes`
- Check table sizes via `pg_total_relation_size()`
- Verify constraint violations in application logs

## Migration Strategy

For production deployments:
1. **Backup existing data** before running migrations
2. **Test migrations** on staging environment first
3. **Run during maintenance windows** for large changes
4. **Monitor performance** after index additions

## Compliance & Auditing

The schema supports:
- **GDPR compliance** through data anonymization
- **Financial auditing** via transaction logs
- **Session verification** through blockchain integration
- **Access logging** for security monitoring

## Support

For schema-related questions or modifications:
- Review model definitions in `/Code/Models/`
- Check business requirements in specification documents
- Test changes on development database first
- Document any custom modifications