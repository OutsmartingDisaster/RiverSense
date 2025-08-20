CREATE TABLE gnss_data (
    id SERIAL PRIMARY KEY,
    raw_data TEXT NOT NULL,
    rinex_file_path VARCHAR,
    processing_status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);