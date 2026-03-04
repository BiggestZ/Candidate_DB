from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.schema.candidate_schema import (
    CandidateCreateRequest,
    CandidateMutationResponse,
    CandidateUpdateRequest,
    CandidateSearchResult,
)
from backend.service.candidate_service import (
    create_candidate,
    delete_candidate,
    search_candidates_for_management,
    update_candidate,
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateSearchResult])
async def list_candidates(
    name: str | None = None,
    role: str | None = None,
    location: str | None = None,
    skill: str | None = None,
    email: str | None = None,
    min_years_experience: int | None = None,
    max_years_experience: int | None = None,
    limit: int = 25,
):
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100.")
        if (
            min_years_experience is not None
            and max_years_experience is not None
            and min_years_experience > max_years_experience
        ):
            raise HTTPException(
                status_code=400,
                detail="min_years_experience cannot be greater than max_years_experience.",
            )

        rows = search_candidates_for_management(
            name=name,
            role=role,
            location=location,
            skill=skill,
            email=email,
            min_years_experience=min_years_experience,
            max_years_experience=max_years_experience,
            limit=limit,
        )
        return [CandidateSearchResult(**row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List candidates error: {str(e)}")


@router.post("", response_model=CandidateMutationResponse)
async def add_candidate(payload: CandidateCreateRequest):
    try:
        candidate_id = create_candidate(payload)
        return CandidateMutationResponse(id=candidate_id, message="Candidate created successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create candidate error: {str(e)}")


@router.put("/{candidate_id}", response_model=CandidateMutationResponse)
async def edit_candidate(candidate_id: UUID, payload: CandidateUpdateRequest):
    try:
        updated = update_candidate(candidate_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Candidate not found.")
        return CandidateMutationResponse(id=candidate_id, message="Candidate updated successfully.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update candidate error: {str(e)}")


@router.delete("/{candidate_id}", response_model=CandidateMutationResponse)
async def remove_candidate(candidate_id: UUID):
    try:
        deleted = delete_candidate(candidate_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Candidate not found.")
        return CandidateMutationResponse(id=candidate_id, message="Candidate deleted successfully.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete candidate error: {str(e)}")
