from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any

# Define actions an agent can take (Expandable)
class AgentAction(str, Enum):
    SEARCH_CANDIDATES = "search_candidates"
    CHAT = "chat"
    UNKNOWN = "unknown"

# Define format of agent results (for logging?)
class AgentResult(BaseModel):
    action: AgentAction
    data: Optional[Any] = None
    message: Optional[str] = None