from uuid import uuid4

from backend.schema.candidate_schema import CandidateCreateRequest, CandidateSearchResult
from backend.schema.search_schema import CandidateSearchParams


def test_candidate_search_result_accepts_backend_payload_shape():
    payload = {
        "id": uuid4(),
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "github_url": None,
        "linkedin_url": "https://linkedin.com/in/jane",
        "website_url": None,
        "location": "New York, NY",
        "years_experience": 8,
        "skills": "Python, FastAPI, PostgreSQL",
        "role": "Senior Backend Engineer",
        "score": 0.88,
    }

    parsed = CandidateSearchResult(**payload)
    assert parsed.role == "Senior Backend Engineer"
    assert parsed.years_experience == 8


def test_candidate_search_params_accepts_list_filters():
    params = CandidateSearchParams(
        semantic_query="senior python backend developer",
        filters={"skills": ["Python", "FastAPI"], "role": "Backend Engineer"},
        limit=10,
    )
    assert params.filters is not None
    assert params.filters["skills"] == ["Python", "FastAPI"]


def test_candidate_create_request_accepts_skills_list():
    payload = CandidateCreateRequest(
        full_name="John Smith",
        email="john@example.com",
        recent_role="Backend Engineer",
        skills=["Python", "PostgreSQL"],
        summary="Strong API and data modeling background.",
    )
    assert payload.skills == ["Python", "PostgreSQL"]
