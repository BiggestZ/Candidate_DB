"""Pydantic Models for the 2 Event types"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

# Template for an LLM Response
class LLMEvent(BaseModel):
    timestamp: datetime
    provider: str
    model: str
    task: str
    prompt_path: str
    raw_response: str
    parsed: Optional[Any] = None
    success: bool
    latency_ms: int

# Template for an Agent Response
class AgentEvent(BaseModel):
    timestamp: datetime
    agent_name: str
    action: str
    input: Any
    output: Any
    success: bool