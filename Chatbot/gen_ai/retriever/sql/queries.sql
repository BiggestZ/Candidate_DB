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
    c.location,
    c.seniority,
    sm.similarity
FROM semantic_matches sm
JOIN candidates c ON c.id = sm.candidate_id
WHERE (:location IS NULL OR c.location = :location)
  AND (:seniority IS NULL OR c.seniority = :seniority)
ORDER BY sm.similarity DESC;
