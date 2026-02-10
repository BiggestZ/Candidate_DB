from anthropic import Anthropic
from llm.base import BaseLLMClient

class AnthropicClient(BaseLLMClient):
    def __init__(self, config):
        super().__init__(config)
        self.client = Anthropic()

    def complete(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.config.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.content[0].text
