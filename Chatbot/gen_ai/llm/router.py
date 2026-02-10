from config import DEFAULT_MODELS, LLMProvider, LLMTask
from llm.providers.openai import OpenAIClient
from llm.providers.anthropic import AnthropicClient
from llm.providers.gemini import GeminiClient

def get_llm_for_task(provider: LLMProvider, task: LLMTask):
    model_config = DEFAULT_MODELS[provider][task]

    # Check if valid providers are present
    if provider == LLMProvider.OPENAI:
        return OpenAIClient(model_config)
    
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicClient(model_config)
    
    elif provider == LLMProvider.GEMINI:
        return GeminiClient(model_config)
    
    # Raise exception for non-valid providers
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")