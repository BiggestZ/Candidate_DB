from database.connection import get_conn


def get_candidate_count() -> int:
    """Return the total number of candidates in the database."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM candidates;")
            result = cur.fetchone()
            return int(result[0]) if result else 0
