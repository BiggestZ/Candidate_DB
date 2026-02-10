BEGIN;

CREATE TABLE IF NOT EXISTS candidate_resume (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    document_type TEXT, -- Resume, Cover Letter, etc
    s3_url TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

COMMIT;