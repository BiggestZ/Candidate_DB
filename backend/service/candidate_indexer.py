from service.embeddings import embed

# Convert a candidate to text
def candidate_to_text(candidate: dict) -> str:
    return f"""
    Name: {candidate.get("name")}
    Location: {candidate.get('location')}
    Seniority: {candidate.get('seniority')}
    Skills: {candidate.get('skills', '')}
    GitHub: {candidate.get('github', '')}
    """

def index_candidate(conn, candidate: dict):
    text = candidate_to_text(candidate)
    embedding = embed(text)

    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO candidates (
            full_name, email, location, seniority,
            github_url, linkedin_url, website_url,
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            candidate["full_name"],
            candidate["email"],
            candidate["location"],
            candidate["seniority"],
            candidate["github_url"],
            candidate["linkedin_url"],
            candidate["website_url"],
        ))

        candidate_id = cur.fetchone()["id"]

        cur.execute("""
            INSERT INTO candidate_embeddings (candidate_id, embedding)
            VALUES (%s, %s)
        """, (candidate_id, embedding))
    
    conn.commit()
    return candidate_id