from typing import Optional, Dict, List
from psycopg2.extras import RealDictCursor

from database.connection import get_conn
from backend.service.embeddings import embed
from backend.schema.candidate_schema import CandidateSearchResult
from backend.schema.search_schema import FilterValue

def search_candidates(
    query: str,
    filters: Optional[Dict[str, FilterValue]] = None,
    limit: int = 10,
) -> List[CandidateSearchResult]:
    """
    Hybrid search over candidates via pgvector + structured filters.
    """
    filters = filters or {}
    role_filter = filters.get("role")
    if isinstance(role_filter, list):
        role_filter = role_filter[0] if role_filter else None

    query_embedding = embed(query)

    sql = """
        SELECT
            c.id,
            c.full_name,
            c.email,
            c.recent_role AS role,
            c.github_url,
            c.linkedin_url,
            c.website_url,
            c.location,
            c.years_experience,
            e.skills,
            1 - (e.embedding <-> %(embedding)s::vector) AS score
        FROM candidates c
        JOIN candidate_profiles e
          ON e.candidate_id = c.id
        WHERE (%(role)s IS NULL OR c.recent_role = %(role)s)
        ORDER BY e.embedding <-> %(embedding)s::vector
        LIMIT %(limit)s;
    """

    params = {
        "embedding": query_embedding,
        "role": role_filter,
        "limit": limit,
    }

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    # handle empty result
    if not rows:
        return []

    return [CandidateSearchResult(**row) for row in rows]
