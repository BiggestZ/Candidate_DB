from pydantic import BaseModel
from typing import Optional, Any

class ChatMessage(BaseModel):
    message: str 
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    intent: str 
    confidence: Optional[float] = None
    data: Optional[dict[str, Any]] = None
