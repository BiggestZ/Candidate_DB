from backend.service.embeddings import embed

# Convert a candidate to text
def candidate_to_text(candidate: dict) -> str:
    skills = candidate.get("skills", [])
    if isinstance(skills, list):
        skills = ", ".join(skills)

    return f"""
    Name: {candidate.get("full_name")}
    Location: {candidate.get('location')}
    Role: {candidate.get('recent_role')}
    Skills: {skills}
    GitHub: {candidate.get('github_url', '')}
    """

def index_candidate(conn, candidate: dict):
    text = candidate_to_text(candidate)
    embedding = embed(text)

    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO candidates (
            full_name, email, recent_role, github_url,
            linkedin_url, website_url, location, years_experience
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            candidate["full_name"],
            candidate["email"],
            candidate["recent_role"],
            candidate["github_url"],
            candidate["linkedin_url"],
            candidate["website_url"],
            candidate.get("location"),
            candidate.get("years_experience"),
        ))

        candidate_id = cur.fetchone()[0]

        skills = candidate.get("skills", [])
        if isinstance(skills, list):
            skills = ", ".join(skills)

        cur.execute("""
            INSERT INTO candidate_profiles (
                candidate_id, summary, skills, experience_years, embedding, embedding_model
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            candidate_id,
            candidate.get("summary", ""),
            skills or "",
            candidate.get("years_experience"),
            embedding,
            "text-embedding-3-small",
        ))
    
    conn.commit()
    return candidate_id
