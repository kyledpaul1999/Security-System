-- Enable the TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Table to store camera information
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rtsp_url VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table to store detection events
CREATE TABLE detection_events (
    time TIMESTAMPTZ NOT NULL,
    camera_id INTEGER NOT NULL REFERENCES cameras(id),
    label VARCHAR(255) NOT NULL,
    confidence REAL,
    bounding_box JSONB,
    PRIMARY KEY (time, camera_id, label)
);

-- Create a hypertable for detection_events
-- This will partition the data by time, which is essential for TimescaleDB performance.
SELECT create_hypertable('detection_events', 'time');

-- Create indexes for faster queries
CREATE INDEX ON detection_events (camer-id, time DESC);
CREATE INDEX ON detection_events (label, time DESC);

-- Insert the cameras from the docker-compose environment variables.
-- This is a bit of a hack, but it's a simple way to get the cameras in the DB.
-- The stream_processor service will read the same environment variable.
-- Note: This part of the script might not be directly executable in a generic SQL client
-- without some pre-processing, but it will work with the docker-entrypoint.
-- However, it is better to handle this in the application logic.
-- For now, I will add some sample cameras.

INSERT INTO cameras (name, rtsp_url) VALUES
('Camera 1', 'rtsp://user:password@192.168.1.64:554/Streaming/Channels/101'),
('Camera 2', 'rtsp://user:password@192.168.1.64:554/Streaming/Channels/201'),
('Camera 3', 'rtsp://user:password@192.168.1.64:554/Streaming/Channels/301');
