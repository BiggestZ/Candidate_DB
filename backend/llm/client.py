from config import LLMProvider, LLMTask
from llm.router import get_llm_for_task

class LLMClient:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
    
    def run(self, *, task: LLMTask, prompt: str) -> str:
        llm = get_llm_for_task(self.provider, task)
        return llm.complete(prompt)