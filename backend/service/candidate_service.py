from uuid import UUID

from psycopg2.extras import RealDictCursor

from database.connection import get_conn
from backend.service.candidate_indexer import candidate_to_text
from backend.service.embeddings import embed
from backend.schema.candidate_schema import CandidateCreateRequest, CandidateUpdateRequest


def _skills_to_csv(skills: list[str] | None) -> str:
    if not skills:
        return ""
    return ", ".join(skill.strip() for skill in skills if skill and skill.strip())


def _skills_from_csv(skills: str | None) -> list[str]:
    if not skills:
        return []
    return [item.strip() for item in skills.split(",") if item.strip()]


def create_candidate(payload: CandidateCreateRequest) -> UUID:
    data = payload.model_dump()
    text = candidate_to_text(data)
    embedding = embed(text)
    skills_csv = _skills_to_csv(payload.skills)

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO candidates (
                    full_name, email, recent_role, github_url,
                    linkedin_url, website_url, location, years_experience
                )
                VALUES (%(full_name)s, %(email)s, %(recent_role)s, %(github_url)s,
                        %(linkedin_url)s, %(website_url)s, %(location)s, %(years_experience)s)
                RETURNING id
                """,
                data,
            )
            candidate_id = cur.fetchone()["id"]

            cur.execute(
                """
                INSERT INTO candidate_profiles (
                    candidate_id, summary, skills, experience_years, embedding, embedding_model
                )
                VALUES (%(candidate_id)s, %(summary)s, %(skills)s, %(experience_years)s,
                        %(embedding)s, %(embedding_model)s)
                """,
                {
                    "candidate_id": candidate_id,
                    "summary": payload.summary or "",
                    "skills": skills_csv,
                    "experience_years": payload.years_experience,
                    "embedding": embedding,
                    "embedding_model": "text-embedding-3-small",
                },
            )

    return candidate_id


def update_candidate(candidate_id: UUID, payload: CandidateUpdateRequest) -> bool:
    updates = payload.model_dump(exclude_unset=True)
    candidate_id_str = str(candidate_id)

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
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
                    cp.summary,
                    cp.skills
                FROM candidates c
                JOIN candidate_profiles cp ON cp.candidate_id = c.id
                WHERE c.id = %(candidate_id)s
                """,
                {"candidate_id": candidate_id_str},
            )
            current = cur.fetchone()
            if not current:
                return False

            merged = {
                "full_name": current["full_name"],
                "email": current["email"],
                "recent_role": current["recent_role"],
                "github_url": current["github_url"],
                "linkedin_url": current["linkedin_url"],
                "website_url": current["website_url"],
                "location": current["location"],
                "years_experience": current["years_experience"],
                "summary": current["summary"],
                "skills": _skills_from_csv(current["skills"]),
            }
            merged.update(updates)

            text = candidate_to_text(merged)
            embedding = embed(text)
            skills_csv = _skills_to_csv(merged.get("skills"))

            cur.execute(
                """
                UPDATE candidates
                SET
                    full_name = %(full_name)s,
                    email = %(email)s,
                    recent_role = %(recent_role)s,
                    github_url = %(github_url)s,
                    linkedin_url = %(linkedin_url)s,
                    website_url = %(website_url)s,
                    location = %(location)s,
                    years_experience = %(years_experience)s
                WHERE id = %(candidate_id)s
                """,
                {**merged, "candidate_id": candidate_id_str},
            )

            cur.execute(
                """
                UPDATE candidate_profiles
                SET
                    summary = %(summary)s,
                    skills = %(skills)s,
                    experience_years = %(experience_years)s,
                    embedding = %(embedding)s,
                    embedding_model = %(embedding_model)s
                WHERE candidate_id = %(candidate_id)s
                """,
                {
                    "candidate_id": candidate_id_str,
                    "summary": merged.get("summary") or "",
                    "skills": skills_csv,
                    "experience_years": merged.get("years_experience"),
                    "embedding": embedding,
                    "embedding_model": "text-embedding-3-small",
                },
            )

    return True


def delete_candidate(candidate_id: UUID) -> bool:
    candidate_id_str = str(candidate_id)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM candidate_profiles WHERE candidate_id = %s", (candidate_id_str,))
            cur.execute("DELETE FROM candidate_resume WHERE candidate_id = %s", (candidate_id_str,))
            cur.execute("DELETE FROM candidates WHERE id = %s", (candidate_id_str,))
            return cur.rowcount > 0


def search_candidates_for_management(
    *,
    name: str | None = None,
    role: str | None = None,
    location: str | None = None,
    skill: str | None = None,
    email: str | None = None,
    min_years_experience: int | None = None,
    max_years_experience: int | None = None,
    limit: int = 25,
) -> list[dict]:
    def pattern(value: str | None) -> str | None:
        return f"%{value.strip()}%" if value and value.strip() else None

    params = {
        "name_pattern": pattern(name),
        "role_pattern": pattern(role),
        "location_pattern": pattern(location),
        "skill_pattern": pattern(skill),
        "email_pattern": pattern(email),
        "min_years_experience": min_years_experience,
        "max_years_experience": max_years_experience,
        "limit": limit,
    }

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
            cp.skills,
            1.0::float AS score
        FROM candidates c
        JOIN candidate_profiles cp
          ON cp.candidate_id = c.id
        WHERE (%(name_pattern)s IS NULL OR c.full_name ILIKE %(name_pattern)s)
          AND (%(role_pattern)s IS NULL OR c.recent_role ILIKE %(role_pattern)s)
          AND (%(location_pattern)s IS NULL OR c.location ILIKE %(location_pattern)s)
          AND (%(skill_pattern)s IS NULL OR cp.skills ILIKE %(skill_pattern)s)
          AND (%(email_pattern)s IS NULL OR c.email ILIKE %(email_pattern)s)
          AND (%(min_years_experience)s IS NULL OR c.years_experience >= %(min_years_experience)s)
          AND (%(max_years_experience)s IS NULL OR c.years_experience <= %(max_years_experience)s)
        ORDER BY c.created_at DESC
        LIMIT %(limit)s;
    """

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
