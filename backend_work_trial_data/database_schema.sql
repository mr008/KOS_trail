-- KOS Backend Engineer Work Trial Database Schema
-- PostgreSQL schema for glucose monitoring data

-- Create database (uncomment if needed)
-- CREATE DATABASE glucose_db;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) UNIQUE NOT NULL,
    age INTEGER CHECK (age > 0 AND age <= 120),
    gender VARCHAR(10) CHECK (gender IN ('M', 'F', 'Other')),
    bmi DECIMAL(4,2) CHECK (bmi > 0 AND bmi <= 100),
    skin_tone VARCHAR(20) CHECK (skin_tone IN ('light', 'medium', 'dark')),
    hba1c DECIMAL(4,2) CHECK (hba1c > 0 AND hba1c <= 20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    serial_number VARCHAR(50) UNIQUE,
    firmware_version VARCHAR(20),
    hardware_revision VARCHAR(20),
    manufacturing_date DATE,
    calibration_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'needs_attention', 'maintenance')),
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Device battery information
CREATE TABLE device_battery_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    current_level INTEGER CHECK (current_level >= 0 AND current_level <= 100),
    estimated_hours_remaining INTEGER CHECK (estimated_hours_remaining >= 0),
    charge_cycles INTEGER DEFAULT 0,
    battery_health VARCHAR(20) CHECK (battery_health IN ('excellent', 'good', 'fair', 'poor')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Device sensor calibration
CREATE TABLE device_sensor_calibration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    red_offset DECIMAL(6,3),
    infrared_offset DECIMAL(6,3),
    green_offset DECIMAL(6,3),
    temperature_offset DECIMAL(6,3),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Device user-specific settings
CREATE TABLE device_user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    skin_tone_compensation VARCHAR(20) CHECK (skin_tone_compensation IN ('light', 'medium', 'dark')),
    motion_sensitivity VARCHAR(20) CHECK (motion_sensitivity IN ('low', 'normal', 'high')),
    sampling_rate VARCHAR(20) CHECK (sampling_rate IN ('standard', 'high_frequency', 'power_save')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Glucose readings table (main data table)
CREATE TABLE glucose_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    glucose_value INTEGER NOT NULL CHECK (glucose_value >= 40 AND glucose_value <= 400),
    confidence DECIMAL(4,3) CHECK (confidence >= 0.0 AND confidence <= 1.0),
    sensor_data JSONB,
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    signal_quality VARCHAR(20) CHECK (signal_quality IN ('excellent', 'good', 'fair', 'poor')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint to prevent duplicate readings for same device at same time
    UNIQUE(device_id, timestamp)
);

-- Alert configurations table
CREATE TABLE alert_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    low_glucose INTEGER DEFAULT 70 CHECK (low_glucose >= 40 AND low_glucose <= 100),
    high_glucose INTEGER DEFAULT 180 CHECK (high_glucose >= 150 AND high_glucose <= 400),
    rapid_change DECIMAL(4,2) DEFAULT 4.0 CHECK (rapid_change >= 1.0 AND rapid_change <= 10.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure low_glucose is less than high_glucose
    CHECK (low_glucose < high_glucose)
);

-- Alert history table
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    device_id VARCHAR(50) REFERENCES devices(device_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('low_glucose', 'high_glucose', 'rapid_change', 'device_offline', 'battery_low')),
    glucose_value INTEGER,
    threshold_value DECIMAL(6,2),
    message TEXT,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Glucose analytics summary table (for performance)
CREATE TABLE glucose_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_glucose DECIMAL(6,2),
    min_glucose INTEGER,
    max_glucose INTEGER,
    time_in_range_percent DECIMAL(5,2),
    readings_count INTEGER DEFAULT 0,
    estimated_a1c DECIMAL(4,2),
    glucose_variability DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, date)
);

-- API audit log table
CREATE TABLE api_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50),
    device_id VARCHAR(50),
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    request_size INTEGER,
    response_size INTEGER,
    duration_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================
-- INDEXES FOR PERFORMANCE
-- =======================

-- Primary query patterns for glucose readings
CREATE INDEX idx_glucose_readings_user_timestamp ON glucose_readings(user_id, timestamp DESC);
CREATE INDEX idx_glucose_readings_device_timestamp ON glucose_readings(device_id, timestamp DESC);
CREATE INDEX idx_glucose_readings_timestamp ON glucose_readings(timestamp DESC);
CREATE INDEX idx_glucose_readings_glucose_value ON glucose_readings(glucose_value);

-- Indexes for device queries
CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);

-- Indexes for alerts
CREATE INDEX idx_alert_history_user_timestamp ON alert_history(user_id, created_at DESC);
CREATE INDEX idx_alert_history_type ON alert_history(alert_type);
CREATE INDEX idx_alert_history_acknowledged ON alert_history(acknowledged);

-- Indexes for analytics
CREATE INDEX idx_glucose_analytics_user_date ON glucose_analytics(user_id, date DESC);

-- Indexes for audit log
CREATE INDEX idx_api_audit_log_timestamp ON api_audit_log(created_at DESC);
CREATE INDEX idx_api_audit_log_user_id ON api_audit_log(user_id);
CREATE INDEX idx_api_audit_log_endpoint ON api_audit_log(endpoint);

-- JSONB index for sensor data queries
CREATE INDEX idx_glucose_readings_sensor_data ON glucose_readings USING GIN (sensor_data);

-- =======================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =======================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_alert_configs_updated_at BEFORE UPDATE ON alert_configs
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_glucose_analytics_updated_at BEFORE UPDATE ON glucose_analytics
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- =======================
-- SAMPLE DATA INSERTION
-- =======================

-- Insert sample users
INSERT INTO users (user_id, age, gender, bmi, skin_tone, hba1c) VALUES
('user_5678', 45, 'F', 24.5, 'medium', 7.2),
('user_9012', 67, 'M', 28.3, 'light', 8.1),
('user_3456', 29, 'F', 22.1, 'dark', 9.5),
('user_7890', 38, 'M', 26.7, 'medium', 6.8),
('user_1357', 52, 'F', 31.2, 'light', 10.1);

-- Insert sample alert configurations
INSERT INTO alert_configs (user_id, low_glucose, high_glucose, rapid_change) VALUES
('user_5678', 70, 180, 4.0),
('user_9012', 65, 200, 5.0),
('user_3456', 75, 250, 6.0),
('user_7890', 70, 160, 3.5),
('user_1357', 80, 300, 8.0);

-- Insert sample devices
INSERT INTO devices (device_id, user_id, serial_number, firmware_version, hardware_revision, manufacturing_date, calibration_date, status, last_seen) VALUES
('ARGUS_001234', 'user_5678', 'ARG2024-001234', '2.1.3', 'Rev C', '2024-12-15', '2025-01-01', 'active', '2025-01-07 17:33:00'),
('ARGUS_002468', 'user_9012', 'ARG2024-002468', '2.1.1', 'Rev B', '2024-11-20', '2024-12-15', 'active', '2025-01-07 17:31:00'),
('ARGUS_003691', 'user_3456', 'ARG2024-003691', '2.1.3', 'Rev C', '2024-10-30', '2024-11-20', 'active', '2025-01-07 17:31:00'),
('ARGUS_004815', 'user_7890', 'ARG2024-004815', '2.1.4', 'Rev C', '2024-12-28', '2024-12-30', 'active', '2025-01-07 17:30:30'),
('ARGUS_005927', 'user_1357', 'ARG2024-005927', '2.0.8', 'Rev A', '2024-09-15', '2024-10-05', 'needs_attention', '2025-01-07 17:30:30');

-- =======================
-- USEFUL QUERY EXAMPLES
-- =======================

-- Get recent glucose readings for a user
/*
SELECT 
    gr.timestamp,
    gr.glucose_value,
    gr.confidence,
    gr.signal_quality,
    d.device_id
FROM glucose_readings gr
JOIN devices d ON gr.device_id = d.device_id
WHERE gr.user_id = 'user_5678'
ORDER BY gr.timestamp DESC
LIMIT 20;
*/

-- Calculate time in range for a user on a specific date
/*
SELECT 
    user_id,
    COUNT(*) as total_readings,
    COUNT(*) FILTER (WHERE glucose_value BETWEEN 70 AND 180) as in_range_readings,
    ROUND(
        (COUNT(*) FILTER (WHERE glucose_value BETWEEN 70 AND 180) * 100.0 / COUNT(*)), 
        2
    ) as time_in_range_percent
FROM glucose_readings 
WHERE user_id = 'user_5678' 
AND DATE(timestamp) = '2025-01-07'
GROUP BY user_id;
*/

-- Find devices with low battery
/*
SELECT 
    d.device_id,
    d.user_id,
    dbi.current_level,
    dbi.battery_health
FROM devices d
JOIN device_battery_info dbi ON d.device_id = dbi.device_id
WHERE dbi.current_level < 30
ORDER BY dbi.current_level ASC;
*/

-- Get glucose trend (rising/falling) for recent readings
/*
SELECT 
    device_id,
    timestamp,
    glucose_value,
    LAG(glucose_value) OVER (PARTITION BY device_id ORDER BY timestamp) as prev_glucose,
    glucose_value - LAG(glucose_value) OVER (PARTITION BY device_id ORDER BY timestamp) as glucose_change
FROM glucose_readings 
WHERE device_id = 'ARGUS_001234'
ORDER BY timestamp DESC
LIMIT 10;
*/

-- =======================
-- PERFORMANCE NOTES
-- =======================

/*
1. The glucose_readings table will be the largest table. Consider partitioning by date for large datasets.
2. The JSONB sensor_data column allows flexible storage but use specific indexes for common queries.
3. The glucose_analytics table provides pre-computed summaries to avoid expensive aggregations.
4. Consider implementing data retention policies to archive old glucose readings.
5. For high-frequency data ingestion, consider using connection pooling and batch inserts.
6. Monitor query performance and add additional indexes based on actual usage patterns.
*/
