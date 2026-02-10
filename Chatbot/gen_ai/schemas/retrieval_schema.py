from pydantic import BaseModel
from typing import Optional, Dict

class RetrievalRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, str]] = None
    limit: int = 10

class RetrievalResponse(BaseModel):
    results: list