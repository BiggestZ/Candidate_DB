BEGIN;

CREATE TABLE IF NOT EXISTS candidate_profiles (
    candidate_id UUID PRIMARY KEY REFERENCES candidate_resume(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    skills TEXT NOT NULL,
    experience_years INT,
    embedding VECTOR(1536) NOT NULL,
    embedding_model TEXT NOT NULL,
    created_at timestamp DEFAULT now()
);
COMMIT;
