CREATE TABLE IF NOT EXISTS study_session_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT,
    completion_status TEXT NOT NULL CHECK (completion_status IN ('completed', 'abandoned')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id),
    UNIQUE(session_id)
);
