-- CareCred Messaging and Notification Tables

-- Create additional enum types for messaging
CREATE TYPE message_type AS ENUM ('text', 'image', 'document', 'system', 'session_update', 'emergency');
CREATE TYPE message_status AS ENUM ('sent', 'delivered', 'read', 'failed');
CREATE TYPE conversation_type AS ENUM ('student_senior', 'student_admin', 'senior_admin', 'admin_admin');
CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent', 'emergency');
CREATE TYPE notification_channel AS ENUM ('email', 'sms', 'push', 'in_app');

-- Conversations table
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_type conversation_type NOT NULL,
    session_id UUID REFERENCES sessions(session_id) ON DELETE SET NULL,
    subject VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Emergency/priority settings
    priority_level notification_priority DEFAULT 'normal',
    requires_admin_attention BOOLEAN DEFAULT FALSE,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    flagged_by UUID REFERENCES users(user_id),
    flagged_at TIMESTAMP WITH TIME ZONE,
    flag_reason TEXT
);

-- Conversation participants
CREATE TABLE conversation_participants (
    participant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    unread_count INTEGER DEFAULT 0 CHECK (unread_count >= 0),
    last_read_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(conversation_id, user_id)
);

-- Messages table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    message_type message_type DEFAULT 'text',
    content TEXT NOT NULL CHECK (LENGTH(content) <= 2000),
    attachment_url TEXT,
    attachment_type VARCHAR(50),
    attachment_size INTEGER CHECK (attachment_size >= 0),
    mime_type VARCHAR(100),
    status message_status DEFAULT 'sent',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- System/automated message fields
    is_system_message BOOLEAN DEFAULT FALSE,
    system_event_type VARCHAR(50),
    related_session_id UUID REFERENCES sessions(session_id) ON DELETE SET NULL,
    
    -- Emergency/flagging
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason VARCHAR(200),
    flagged_by UUID REFERENCES users(user_id),
    flagged_at TIMESTAMP WITH TIME ZONE,
    
    -- Encryption and security
    content_encrypted BOOLEAN DEFAULT FALSE,
    encryption_key_id VARCHAR(100)
);

-- Message read receipts
CREATE TABLE message_read_receipts (
    receipt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    device_info JSONB,
    
    UNIQUE(message_id, user_id)
);

-- User notification preferences
CREATE TABLE notification_preferences (
    preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- General notification channels
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    in_app_notifications BOOLEAN DEFAULT TRUE,
    
    -- Specific notification types
    session_reminders BOOLEAN DEFAULT TRUE,
    session_updates BOOLEAN DEFAULT TRUE,
    new_messages BOOLEAN DEFAULT TRUE,
    credit_updates BOOLEAN DEFAULT TRUE,
    admin_announcements BOOLEAN DEFAULT TRUE,
    emergency_alerts BOOLEAN DEFAULT TRUE,
    rating_requests BOOLEAN DEFAULT TRUE,
    
    -- Timing preferences
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- System notifications
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL CHECK (LENGTH(message) <= 1000),
    notification_type VARCHAR(50) NOT NULL,
    priority notification_priority DEFAULT 'normal',
    related_entity_type VARCHAR(50), -- session, message, credit, user, etc.
    related_entity_id UUID,
    action_url TEXT,
    action_text VARCHAR(100),
    
    -- Status tracking
    is_read BOOLEAN DEFAULT FALSE,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_via JSONB DEFAULT '[]'::jsonb, -- array of channels used
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery tracking per channel
    email_delivered BOOLEAN DEFAULT FALSE,
    email_opened BOOLEAN DEFAULT FALSE,
    sms_delivered BOOLEAN DEFAULT FALSE,
    push_delivered BOOLEAN DEFAULT FALSE,
    push_opened BOOLEAN DEFAULT FALSE,
    
    -- Retry and error handling
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    last_error TEXT
);

-- Emergency alerts
CREATE TABLE emergency_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiated_by UUID NOT NULL REFERENCES users(user_id),
    alert_type VARCHAR(20) CHECK (alert_type IN ('medical', 'safety', 'technical', 'other')),
    severity notification_priority DEFAULT 'high',
    location TEXT,
    session_id UUID REFERENCES sessions(session_id) ON DELETE SET NULL,
    message TEXT NOT NULL CHECK (LENGTH(message) <= 1000),
    
    -- Emergency contacts and responders
    emergency_contacts_notified JSONB DEFAULT '[]'::jsonb,
    admin_responders JSONB DEFAULT '[]'::jsonb,
    external_services_contacted JSONB DEFAULT '[]'::jsonb, -- 911, etc.
    
    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id),
    resolution_notes TEXT,
    
    -- Escalation tracking
    escalated BOOLEAN DEFAULT FALSE,
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalated_by UUID REFERENCES users(user_id),
    escalation_reason TEXT
);

-- Message threads for organization
CREATE TABLE message_threads (
    thread_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    subject VARCHAR(200) NOT NULL,
    participant_count INTEGER NOT NULL CHECK (participant_count >= 2),
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]'::jsonb,
    
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notification delivery attempts log
CREATE TABLE notification_delivery_log (
    delivery_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications(notification_id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    external_reference_id VARCHAR(200), -- provider message ID
    cost_cents INTEGER CHECK (cost_cents >= 0), -- for SMS/email cost tracking
    
    -- Provider-specific data
    provider_name VARCHAR(50),
    provider_response JSONB
);

-- Message attachments
CREATE TABLE message_attachments (
    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    attachment_type VARCHAR(20) CHECK (attachment_type IN ('image', 'document', 'video', 'audio')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    virus_scanned BOOLEAN DEFAULT FALSE,
    virus_scan_result VARCHAR(20),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Auto-moderation and content filtering
CREATE TABLE message_moderation (
    moderation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    flagged_content TEXT,
    flag_type VARCHAR(50) NOT NULL, -- profanity, harassment, spam, etc.
    confidence_score DECIMAL(5, 4) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    auto_action VARCHAR(20) CHECK (auto_action IN ('none', 'flag', 'hide', 'delete')),
    admin_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by UUID REFERENCES users(user_id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    admin_action VARCHAR(20),
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add triggers for updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_updated_at BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update conversation last_message_at
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET last_message_at = NEW.sent_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE conversation_id = NEW.conversation_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update conversation when new message is sent
CREATE TRIGGER update_conversation_on_new_message
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_last_message();

-- Function to update unread counts
CREATE OR REPLACE FUNCTION update_unread_counts()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment unread count for all participants except sender
    UPDATE conversation_participants 
    SET unread_count = unread_count + 1
    WHERE conversation_id = NEW.conversation_id 
    AND user_id != NEW.sender_id 
    AND is_active = TRUE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update unread counts on new message
CREATE TRIGGER update_unread_counts_on_message
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_unread_counts();

-- Function to reset unread count when user reads messages
CREATE OR REPLACE FUNCTION reset_unread_count(
    p_conversation_id UUID,
    p_user_id UUID
) RETURNS void AS $$
BEGIN
    UPDATE conversation_participants 
    SET unread_count = 0,
        last_read_at = CURRENT_TIMESTAMP
    WHERE conversation_id = p_conversation_id 
    AND user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to check if user is in quiet hours
CREATE OR REPLACE FUNCTION is_in_quiet_hours(
    p_user_id UUID,
    p_check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) RETURNS BOOLEAN AS $$
DECLARE
    preferences notification_preferences%ROWTYPE;
    user_time TIME;
    quiet_start TIME;
    quiet_end TIME;
BEGIN
    -- Get user preferences
    SELECT * INTO preferences 
    FROM notification_preferences 
    WHERE user_id = p_user_id;
    
    IF NOT FOUND THEN
        RETURN FALSE; -- No preferences set, assume not in quiet hours
    END IF;
    
    -- Convert to user's timezone (simplified - in reality would use proper timezone conversion)
    user_time := p_check_time::TIME;
    quiet_start := preferences.quiet_hours_start;
    quiet_end := preferences.quiet_hours_end;
    
    -- Check if current time is within quiet hours
    IF quiet_start <= quiet_end THEN
        -- Normal case (e.g., 22:00 to 08:00 next day)
        RETURN user_time >= quiet_start AND user_time <= quiet_end;
    ELSE
        -- Overnight case (e.g., 22:00 to 08:00)
        RETURN user_time >= quiet_start OR user_time <= quiet_end;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to create system message
CREATE OR REPLACE FUNCTION create_system_message(
    p_conversation_id UUID,
    p_event_type VARCHAR,
    p_content TEXT,
    p_session_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    message_id UUID;
    system_user_id UUID := '00000000-0000-0000-0000-000000000000'; -- Special system user ID
BEGIN
    INSERT INTO messages (
        conversation_id,
        sender_id,
        message_type,
        content,
        is_system_message,
        system_event_type,
        related_session_id,
        status
    ) VALUES (
        p_conversation_id,
        system_user_id,
        'system',
        p_content,
        TRUE,
        p_event_type,
        p_session_id,
        'delivered'
    ) RETURNING message_id INTO message_id;
    
    RETURN message_id;
END;
$$ LANGUAGE plpgsql;