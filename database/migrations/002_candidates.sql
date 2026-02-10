BEGIN;

CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    recent_role TEXT NOT NULL,
    github_url TEXT,
    linkedin_url TEXT,
    website_url TEXT,
    location TEXT,
    years_experience INT,
    created_at TIMESTAMP DEFAULT now()
);

COMMIT;