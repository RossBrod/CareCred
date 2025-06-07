-- CareCred Messaging and Communication Tables - Normalized
-- Comprehensive messaging system with proper relationships

-- =====================================================
-- CORE MESSAGING TABLES
-- =====================================================

-- Conversations - container for related messages
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Conversation identification
    conversation_number VARCHAR(20) UNIQUE, -- Human-readable conversation number
    subject VARCHAR(200),
    conversation_type VARCHAR(50) NOT NULL CHECK (conversation_type IN (
        'student_senior', 'student_admin', 'senior_admin', 'admin_admin', 
        'session_discussion', 'support_ticket', 'emergency_thread'
    )),
    
    -- Context and relationships
    session_id UUID REFERENCES sessions(session_id) ON DELETE SET NULL,
    related_entity_type VARCHAR(50), -- credit, disbursement, alert, etc.
    related_entity_id UUID,
    
    -- Status and lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    archived_by UUID REFERENCES users(user_id),
    
    -- Priority and special handling
    priority_level notification_priority DEFAULT 'normal',
    requires_admin_attention BOOLEAN DEFAULT FALSE,
    is_emergency BOOLEAN DEFAULT FALSE,
    
    -- Moderation and flags
    is_flagged BOOLEAN DEFAULT FALSE,
    flagged_reason TEXT,
    flagged_by UUID REFERENCES users(user_id),
    flagged_at TIMESTAMP WITH TIME ZONE,
    
    -- Auto-close settings
    auto_close_after_hours INTEGER, -- Auto-close inactive conversations
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation participants - who can see and participate
CREATE TABLE conversation_participants (
    participant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Participation details
    role VARCHAR(20) DEFAULT 'participant' CHECK (role IN ('owner', 'participant', 'observer', 'moderator')),
    can_send_messages BOOLEAN DEFAULT TRUE,
    can_add_participants BOOLEAN DEFAULT FALSE,
    
    -- Status tracking
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Message tracking
    unread_count INTEGER DEFAULT 0 CHECK (unread_count >= 0),
    last_read_message_id UUID, -- Will reference messages table
    last_read_at TIMESTAMP WITH TIME ZONE,
    
    -- Notification preferences for this conversation
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    UNIQUE(conversation_id, user_id)
);

-- Messages - individual messages within conversations
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Message identification
    message_number VARCHAR(30) UNIQUE, -- Human-readable message number
    
    -- Message content
    message_type message_type DEFAULT 'text',
    content TEXT NOT NULL CHECK (LENGTH(content) <= 4000),
    content_plain TEXT, -- Plain text version for search and notifications
    
    -- Threading and replies
    parent_message_id UUID REFERENCES messages(message_id),
    thread_depth INTEGER DEFAULT 0 CHECK (thread_depth >= 0),
    
    -- Status and delivery
    status message_status DEFAULT 'sent',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    
    -- System and automated messages
    is_system_message BOOLEAN DEFAULT FALSE,
    system_event_type VARCHAR(50), -- session_started, credit_earned, etc.
    
    -- Content moderation
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason VARCHAR(200),
    flagged_by UUID REFERENCES users(user_id),
    flagged_at TIMESTAMP WITH TIME ZONE,
    moderation_status VARCHAR(20) DEFAULT 'approved' CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'hidden')),
    
    -- Message metadata
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES users(user_id),
    
    -- Priority and special handling
    is_urgent BOOLEAN DEFAULT FALSE,
    requires_response BOOLEAN DEFAULT FALSE,
    response_due_at TIMESTAMP WITH TIME ZONE,
    
    -- Device and location context
    sent_from_device_type VARCHAR(20), -- ios, android, web, api
    sent_from_ip INET,
    sent_from_location_id UUID REFERENCES gps_locations(location_id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message attachments - files, images, documents
CREATE TABLE message_attachments (
    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    
    -- File information
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    
    -- Attachment classification
    attachment_type VARCHAR(20) NOT NULL CHECK (attachment_type IN ('image', 'document', 'video', 'audio', 'other')),
    
    -- Image-specific metadata
    image_width INTEGER CHECK (image_width > 0),
    image_height INTEGER CHECK (image_height > 0),
    thumbnail_url TEXT,
    
    -- Security and verification
    virus_scanned BOOLEAN DEFAULT FALSE,
    virus_scan_result VARCHAR(20) DEFAULT 'pending' CHECK (virus_scan_result IN ('pending', 'clean', 'infected', 'failed')),
    content_hash VARCHAR(255), -- For deduplication and integrity
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    access_expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0,
    
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Content restrictions
    is_sensitive BOOLEAN DEFAULT FALSE, -- Contains sensitive information
    requires_verification BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- MESSAGE READ TRACKING
-- =====================================================

-- Message read receipts - detailed read tracking
CREATE TABLE message_read_receipts (
    receipt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Read details
    read_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_duration_seconds INTEGER, -- How long user viewed the message
    
    -- Device context
    device_type VARCHAR(20),
    device_info JSONB DEFAULT '{}'::jsonb,
    read_from_ip INET,
    
    UNIQUE(message_id, user_id)
);

-- =====================================================
-- NOTIFICATION SYSTEM
-- =====================================================

-- User notification preferences - comprehensive settings
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Channel preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    in_app_notifications BOOLEAN DEFAULT TRUE,
    
    -- Message notification settings
    notify_new_messages BOOLEAN DEFAULT TRUE,
    notify_message_replies BOOLEAN DEFAULT TRUE,
    notify_mentions BOOLEAN DEFAULT TRUE,
    notify_urgent_messages BOOLEAN DEFAULT TRUE,
    
    -- Session notification settings
    notify_session_requests BOOLEAN DEFAULT TRUE,
    notify_session_confirmations BOOLEAN DEFAULT TRUE,
    notify_session_reminders BOOLEAN DEFAULT TRUE,
    notify_session_updates BOOLEAN DEFAULT TRUE,
    notify_session_cancellations BOOLEAN DEFAULT TRUE,
    
    -- Credit and financial notifications
    notify_credit_earned BOOLEAN DEFAULT TRUE,
    notify_disbursements BOOLEAN DEFAULT TRUE,
    notify_payment_updates BOOLEAN DEFAULT TRUE,
    
    -- Administrative notifications
    notify_admin_announcements BOOLEAN DEFAULT TRUE,
    notify_policy_updates BOOLEAN DEFAULT TRUE,
    notify_system_maintenance BOOLEAN DEFAULT TRUE,
    
    -- Emergency and safety notifications
    notify_emergency_alerts BOOLEAN DEFAULT TRUE,
    notify_safety_concerns BOOLEAN DEFAULT TRUE,
    
    -- Timing preferences
    quiet_hours_enabled BOOLEAN DEFAULT FALSE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Frequency controls
    digest_mode_enabled BOOLEAN DEFAULT FALSE, -- Batch notifications
    digest_frequency VARCHAR(20) DEFAULT 'daily' CHECK (digest_frequency IN ('hourly', 'daily', 'weekly')),
    max_notifications_per_hour INTEGER DEFAULT 10,
    
    -- Contact preferences
    preferred_contact_language VARCHAR(10) DEFAULT 'en',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System notifications - app notifications and alerts
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Notification content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL CHECK (LENGTH(message) <= 2000),
    notification_type VARCHAR(50) NOT NULL,
    priority notification_priority DEFAULT 'normal',
    
    -- Related entity
    related_entity_type VARCHAR(50), -- session, message, credit, user, etc.
    related_entity_id UUID,
    
    -- Action handling
    action_url TEXT,
    action_text VARCHAR(100),
    requires_action BOOLEAN DEFAULT FALSE,
    action_completed BOOLEAN DEFAULT FALSE,
    action_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery status
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE,
    sent_via JSONB DEFAULT '[]'::jsonb, -- Array of channels used
    
    -- Read status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Lifecycle
    expires_at TIMESTAMP WITH TIME ZONE,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    
    -- Retry and error handling
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notification delivery tracking - per channel delivery details
CREATE TABLE notification_delivery_log (
    delivery_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications(notification_id) ON DELETE CASCADE,
    
    -- Delivery channel
    channel notification_channel NOT NULL,
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    
    -- Status and timing
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced', 'opened')),
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    
    -- Provider details
    provider_name VARCHAR(50), -- sendgrid, twilio, firebase, etc.
    provider_message_id VARCHAR(200),
    provider_response JSONB DEFAULT '{}'::jsonb,
    
    -- Cost tracking
    cost_cents INTEGER CHECK (cost_cents >= 0),
    
    -- Error handling
    error_code VARCHAR(50),
    error_message TEXT,
    
    -- Recipient details (for audit)
    recipient_address VARCHAR(255), -- email, phone, device token
    recipient_masked VARCHAR(255) -- Masked version for logs
);

-- =====================================================
-- EMERGENCY AND SPECIAL COMMUNICATIONS
-- =====================================================

-- Emergency alerts - critical safety communications
CREATE TABLE emergency_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Alert identification
    alert_number VARCHAR(20) UNIQUE, -- Human-readable emergency number
    
    -- Source and context
    initiated_by UUID NOT NULL REFERENCES users(user_id),
    session_id UUID REFERENCES sessions(session_id) ON DELETE SET NULL,
    location_id UUID REFERENCES gps_locations(location_id),
    
    -- Alert details
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('medical', 'safety', 'technical', 'suspicious_activity', 'other')),
    severity notification_priority DEFAULT 'urgent',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL CHECK (LENGTH(description) <= 2000),
    
    -- Emergency contacts and responses
    emergency_contacts_notified JSONB DEFAULT '[]'::jsonb,
    admin_responders JSONB DEFAULT '[]'::jsonb,
    external_services_contacted JSONB DEFAULT '[]'::jsonb, -- 911, police, etc.
    
    -- Status and resolution
    is_active BOOLEAN DEFAULT TRUE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_summary TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id),
    
    -- Escalation tracking
    escalation_level INTEGER DEFAULT 1 CHECK (escalation_level >= 1 AND escalation_level <= 5),
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalated_by UUID REFERENCES users(user_id),
    escalation_reason TEXT,
    
    -- Follow-up requirements
    requires_follow_up BOOLEAN DEFAULT FALSE,
    follow_up_due_at TIMESTAMP WITH TIME ZONE,
    follow_up_completed BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CONTENT MODERATION
-- =====================================================

-- Message moderation and content filtering
CREATE TABLE message_moderation (
    moderation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    
    -- Automated detection
    auto_flagged BOOLEAN DEFAULT FALSE,
    auto_flag_reason VARCHAR(100),
    confidence_score DECIMAL(5, 4) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    detected_categories JSONB DEFAULT '[]'::jsonb, -- profanity, harassment, spam, etc.
    
    -- Automated actions
    auto_action VARCHAR(20) DEFAULT 'none' CHECK (auto_action IN ('none', 'flag', 'hide', 'delete', 'quarantine')),
    auto_action_taken_at TIMESTAMP WITH TIME ZONE,
    
    -- Human review
    requires_human_review BOOLEAN DEFAULT FALSE,
    human_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by UUID REFERENCES admin_profiles(user_id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewer_decision VARCHAR(20) CHECK (reviewer_decision IN ('approved', 'rejected', 'escalated', 'requires_edit')),
    reviewer_notes TEXT,
    
    -- Action taken
    final_action VARCHAR(20) CHECK (final_action IN ('none', 'approved', 'hidden', 'deleted', 'edited', 'warned')),
    action_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User communication restrictions - temporary communication limits
CREATE TABLE user_communication_restrictions (
    restriction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Restriction details
    restriction_type VARCHAR(20) NOT NULL CHECK (restriction_type IN ('mute', 'limited', 'monitoring', 'banned')),
    reason TEXT NOT NULL,
    
    -- Scope of restriction
    applies_to_messages BOOLEAN DEFAULT TRUE,
    applies_to_attachments BOOLEAN DEFAULT TRUE,
    applies_to_new_conversations BOOLEAN DEFAULT FALSE,
    
    -- Duration
    effective_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_permanent BOOLEAN DEFAULT FALSE,
    
    -- Administration
    imposed_by UUID NOT NULL REFERENCES admin_profiles(user_id),
    appeal_allowed BOOLEAN DEFAULT TRUE,
    appeal_submitted BOOLEAN DEFAULT FALSE,
    appeal_text TEXT,
    appeal_submitted_at TIMESTAMP WITH TIME ZONE,
    appeal_reviewed_by UUID REFERENCES admin_profiles(user_id),
    appeal_decision VARCHAR(20) CHECK (appeal_decision IN ('approved', 'denied', 'modified')),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    lifted_at TIMESTAMP WITH TIME ZONE,
    lifted_by UUID REFERENCES admin_profiles(user_id),
    lift_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Conversations indexes
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_active ON conversations(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_conversations_flagged ON conversations(is_flagged) WHERE is_flagged = TRUE;
CREATE INDEX idx_conversations_last_activity ON conversations(last_activity_at);

-- Participants indexes
CREATE INDEX idx_conversation_participants_conversation ON conversation_participants(conversation_id);
CREATE INDEX idx_conversation_participants_user ON conversation_participants(user_id);
CREATE INDEX idx_conversation_participants_active ON conversation_participants(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_conversation_participants_unread ON conversation_participants(unread_count) WHERE unread_count > 0;

-- Messages indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
CREATE INDEX idx_messages_parent ON messages(parent_message_id);
CREATE INDEX idx_messages_system ON messages(is_system_message) WHERE is_system_message = TRUE;
CREATE INDEX idx_messages_flagged ON messages(is_flagged) WHERE is_flagged = TRUE;
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('english', content_plain));

-- Attachments indexes
CREATE INDEX idx_message_attachments_message ON message_attachments(message_id);
CREATE INDEX idx_message_attachments_type ON message_attachments(attachment_type);
CREATE INDEX idx_message_attachments_uploaded_at ON message_attachments(uploaded_at);

-- Notifications indexes
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_entity ON notifications(related_entity_type, related_entity_id);
CREATE INDEX idx_notifications_expires_at ON notifications(expires_at);

-- Emergency alerts indexes
CREATE INDEX idx_emergency_alerts_initiated_by ON emergency_alerts(initiated_by);
CREATE INDEX idx_emergency_alerts_session ON emergency_alerts(session_id);
CREATE INDEX idx_emergency_alerts_type_severity ON emergency_alerts(alert_type, severity);
CREATE INDEX idx_emergency_alerts_active ON emergency_alerts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_emergency_alerts_created_at ON emergency_alerts(created_at);

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Auto-generate conversation numbers
CREATE OR REPLACE FUNCTION generate_conversation_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.conversation_number := 'CONV-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                              LPAD(NEXTVAL('conversation_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE conversation_number_seq START 1;

CREATE TRIGGER generate_conversation_number_trigger
    BEFORE INSERT ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION generate_conversation_number();

-- Auto-generate message numbers
CREATE OR REPLACE FUNCTION generate_message_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.message_number := 'MSG-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                         LPAD(NEXTVAL('message_number_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE message_number_seq START 1;

CREATE TRIGGER generate_message_number_trigger
    BEFORE INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION generate_message_number();

-- Auto-generate emergency alert numbers
CREATE OR REPLACE FUNCTION generate_alert_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.alert_number := 'ALERT-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                       LPAD(NEXTVAL('alert_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE alert_number_seq START 1;

CREATE TRIGGER generate_alert_number_trigger
    BEFORE INSERT ON emergency_alerts
    FOR EACH ROW
    EXECUTE FUNCTION generate_alert_number();

-- Update conversation last activity when messages are sent
CREATE OR REPLACE FUNCTION update_conversation_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET last_activity_at = NEW.sent_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE conversation_id = NEW.conversation_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_activity_trigger
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_activity();

-- Update unread counts when messages are sent
CREATE OR REPLACE FUNCTION update_unread_counts()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment unread count for all active participants except sender
    UPDATE conversation_participants 
    SET unread_count = unread_count + 1
    WHERE conversation_id = NEW.conversation_id 
    AND user_id != NEW.sender_id 
    AND is_active = TRUE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_unread_counts_trigger
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_unread_counts();

-- Generate plain text content for search
CREATE OR REPLACE FUNCTION extract_plain_text()
RETURNS TRIGGER AS $$
BEGIN
    -- Simple HTML/markdown removal - in production would use proper parsing
    NEW.content_plain := regexp_replace(NEW.content, '<[^>]*>', '', 'g');
    NEW.content_plain := regexp_replace(NEW.content_plain, '\*\*([^*]+)\*\*', '\1', 'g'); -- Bold
    NEW.content_plain := regexp_replace(NEW.content_plain, '\*([^*]+)\*', '\1', 'g'); -- Italic
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER extract_plain_text_trigger
    BEFORE INSERT OR UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION extract_plain_text();

-- Add updated_at triggers
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_updated_at BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emergency_alerts_updated_at BEFORE UPDATE ON emergency_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();