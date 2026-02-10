from openai import OpenAI
from llm.base import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    def __init__(self, config):
        super().__init__(config)
        self.client = OpenAI()

    def complete(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.config.model_name,
            input=prompt,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
        )
        return response.output_text
