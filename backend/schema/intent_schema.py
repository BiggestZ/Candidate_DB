from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from backend.schema.search_schema import CandidateSearchParams

class IntentType(str, Enum):
    search = "search"
    chat = "chat"
    unknown = "unknown"

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

    @model_validator(mode="after")
    def validate_search_params(self) -> "Intent":
        if self.intent == IntentType.search:
            if self.search_params is None:
                raise ValueError("search_params is required when intent is 'search'.")
        else:
            if self.search_params is not None:
                raise ValueError("search_params must be null unless intent is 'search'.")
        return self
