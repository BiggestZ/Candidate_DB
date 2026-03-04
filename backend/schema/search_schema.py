from pydantic import BaseModel, Field
from typing import Optional, Dict

FilterValue = str | list[str]

class CandidateSearchParams(BaseModel):
    semantic_query: str = Field(min_length=5)
    filters: Optional[Dict[str, FilterValue]] = None
    limit: int = Field(default=10, ge=1, le=25)
