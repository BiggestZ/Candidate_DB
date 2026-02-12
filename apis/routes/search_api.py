from fastapi import APIRouter, HTTPException
from typing import List
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from Chatbot.gen_ai.retriever.search import search_candidates
from Chatbot.gen_ai.schemas.candidate_schema import CandidateSearchResult
from Chatbot.gen_ai.schemas.search_schema import CandidateSearchParams

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=List[CandidateSearchResult])
async def search(payload: CandidateSearchParams):
    """
    Direct search endpoint for finding candidates.
    Uses semantic search with optional filters.
    """
    try:
        results = search_candidates(
            query=payload.semantic_query,
            filters=payload.filters,
            limit=payload.limit
        )
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")