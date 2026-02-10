"""
This file holds the config for all LLM models. 
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

# Define LLM Providers
class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

# Define different possible tasks for LLM
class LLMTask(str, Enum):
    INTENT = 'intent'
    CHAT = 'chat'
    REASONING = 'reasoning'

# Configure model settings
class ModelConfig(BaseModel):
    """Config for a specific model"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.7 # Determines randomness of model output
    max_tokens: int = 1000
    top_p: float = 1.0 # sampling temperature, 1.0 is more random, 0.0 is more deterministic
    frequency_penalty: float = 0.0 # Penalty for repeated tokens
    presence_penalty: float = 0.0 # 

# Define how model type/parameters change for different task types.
DEFAULT_MODELS: dict[LLMProvider, dict[LLMTask, ModelConfig]] = {
    LLMProvider.OPENAI: {
        LLMTask.intent: ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4.1-mini",
            temperature=0.0,
            max_tokens=1000
        ),
        LLMTask.CHAT: ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o",
            temperature=0.7,
            max_tokens=1000
        )
    },
    LLMProvider.ANTHROPIC: {
        LLMTask.intent: ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="claude-3-haiku",
            temperature=0.0,
            max_tokens=1000
        ),
        LLMTask.CHAT: ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="claude-sonnet-4-5-1106",
            temperature=0.7,
            max_tokens=1000
        )
    },
    LLMProvider.GEMINI: {
        LLMTask.INTENT: ModelConfig(
            provider=LLMProvider.GEMINI,
            model_name="gemini-2.0-flash-exp",
            temperature=0.0
        ),
        LLMTask.CHAT: ModelConfig(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-pro",
            temperature=0.7
        ),
    },
}