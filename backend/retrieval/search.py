from typing import Optional, Dict, List
import os, sys
import psycopg2

project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
#print(project_root)
sys.path.insert(0, project_root)

from database.connection import get_conn
from backend.service.embeddings import embed
from backend.schema.candidate_schema import CandidateSearchResult

def search_candidates(
    query: str,
    filters: Optional[Dict[str, str]] = None,
    limit: int = 10,
) -> List [CandidateSearchResult]:
    """
    Hybrid search over candidates via pgvector + structed filters
    """
    filters = filters or {}

    query_embedding = embed(query)

    sql = """
        SELECT
            c.id,
            c.full_name,
            c.email,
            c.recent_role,
            c.github_url,
            c.linkedin_url,
            c.website_url,
            c.location,
            c.years_experience,
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
        "role": filters.get("role"),
        "limit": limit,
    }

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    # handle empty result
    if not rows:
        return []
    
    # Debug: print 1st row to verify structure
    print(f"Found {len(rows)} results.")
    if rows:
        print(f"First row: {rows[0].keys()}")  
    
    return [CandidateSearchResult(**row) for row in rows]