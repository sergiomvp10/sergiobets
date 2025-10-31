
CREATE TABLE IF NOT EXISTS scheduled_notifications (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(255) NOT NULL,
    notify_type VARCHAR(20) NOT NULL CHECK (notify_type IN ('morning', 'prematch')),
    scheduled_at TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    kickoff_utc TIMESTAMPTZ NOT NULL,
    home_team VARCHAR(255),
    away_team VARCHAR(255),
    league VARCHAR(255),
    prediction_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(match_id, notify_type)
);

CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_scheduled_at ON scheduled_notifications(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_sent_at ON scheduled_notifications(sent_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_notify_type ON scheduled_notifications(notify_type);

COMMENT ON TABLE scheduled_notifications IS 'Tracks scheduled and sent prediction notifications to prevent duplicates';
COMMENT ON COLUMN scheduled_notifications.match_id IS 'Unique identifier for the match (from FootyStats API)';
COMMENT ON COLUMN scheduled_notifications.notify_type IS 'Type of notification: morning (6:59 AM) or prematch (2 hours before)';
COMMENT ON COLUMN scheduled_notifications.scheduled_at IS 'When the notification is scheduled to be sent (UTC)';
COMMENT ON COLUMN scheduled_notifications.sent_at IS 'When the notification was actually sent (NULL if not sent yet)';
COMMENT ON COLUMN scheduled_notifications.kickoff_utc IS 'Match kickoff time in UTC';
COMMENT ON COLUMN scheduled_notifications.prediction_data IS 'JSON snapshot of the prediction message for morning picks';
