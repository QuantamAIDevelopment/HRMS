CREATE TABLE IF NOT EXISTS job_titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    department VARCHAR(100),
    level VARCHAR(50),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_job_titles_title ON job_titles(title);