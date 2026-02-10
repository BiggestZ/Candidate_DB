BEGIN;

CREATE INDEX candidate_resume_embedding_idx
ON candidate_profiles
USING ivfflat(embedding vector_cosine_ops)
WITH (lists = 100);

COMMIT;