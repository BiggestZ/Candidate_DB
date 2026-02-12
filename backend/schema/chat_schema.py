from pydantic import BaseModel
from typing import Optional, Any
import os, sys

from pydantic_core.core_schema import NoneSchema

project_root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
print("CWD: ",project_root)
sys.path.insert(0, project_root)

from agents.types import AgentAction

class ChatMessage(BaseModel):
    message: str 
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    intent: str 
    confidence: Optional[float] = None
    data: Optional[dict[str, Any]] = None