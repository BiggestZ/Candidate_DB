-- This File contains the SQL needed to run the semantic search (Will breakdown later)
WITH semantic_matches AS (
    SELECT
        candidate_id,
        1 - (embedding <=> :query_embedding) AS similarity
    FROM candidate_profiles
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> :query_embedding
    LIMIT :semantic_limit
)
SELECT
    c.id,
    c.full_name,
    c.email,
    c.recent_role AS role,
    c.location,
    c.years_experience,
    c.github_url,
    c.linkedin_url,
    c.website_url,
    c.created_at,
    cp.skills,
    sm.similarity
FROM semantic_matches sm
JOIN candidates c ON c.id = sm.candidate_id
JOIN candidate_profiles cp ON cp.candidate_id = c.id
WHERE (:location IS NULL OR c.location = :location)
  AND (:role IS NULL OR c.recent_role = :role)
ORDER BY sm.similarity DESC;
