from openai import OpenAI
from llm.base import BaseLLMClient
from dotenv import load_dotenv
import os

load_dotenv()

class OpenAIClient(BaseLLMClient):
    def __init__(self, config):
        super().__init__(config)
        self.client = OpenAI(api_key=os.getenv("OPENAI"))

    def complete(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.config.model_name,
            input=prompt,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
        )
        return response.output_text
