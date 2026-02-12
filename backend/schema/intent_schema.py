from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
import os, sys

project_root=os.path.abspath(os.path.join(os.path.dirname(__file__)))
# print("ROOT: ",project_root)
sys.path.insert(0, project_root)

from search_schema import CandidateSearchParams

class IntentType(str, Enum):
    search = "search"
    chat = "chat"

class IntentSource(str, Enum):
    keyword = "keyword"
    llm = "llm"
    fallback = "fallback"

class Intent(BaseModel):
    intent: IntentType = Field(
        ...,
        description="The classified user intent"
    )
    source: IntentSource = Field(
        ...,
        description="How intent was determined"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for intent."
    )
    reason: Optional[str] = Field(
        None,
        description="Short explanation for debuggin only."
    )
    search_params: Optional[CandidateSearchParams] = Field(
        None,
        description="Contains all data needed for search if intent is search."
    )
    