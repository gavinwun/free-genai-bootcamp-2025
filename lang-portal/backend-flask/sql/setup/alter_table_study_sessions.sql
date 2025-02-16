-- Add status column if it doesn't exist
ALTER TABLE study_sessions ADD COLUMN status TEXT CHECK (status IN ('completed', 'abandoned'));

-- Add not null constraint to status column
ALTER TABLE study_sessions ALTER COLUMN status SET NOT NULL DEFAULT 'abandoned';

-- Add not null constraint to status column
ALTER TABLE study_sessions ALTER COLUMN status DROP DEFAULT;
