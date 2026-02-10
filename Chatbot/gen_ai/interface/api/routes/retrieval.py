from fastapi import APIRouter
from schemas.retrieval import RetrievalRequest, RetrievalResponse
from agents.retrieval_agent import RetrievalAgent

router = APIRouter(prefix="/retrieval", tags=["retrieval"])

retrieval_agent = RetrievalAgent()

@router.post("", response_model=RetrievalResponse)
def search_candidate(payload: RetrievalRequest):
    results = retrieval_agent.run(
        query=payload.query,
        filters=payload.filters,
        limit=payload.limit
    )
    return {"results": results}