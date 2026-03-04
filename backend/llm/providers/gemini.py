import google.genai as genai
from backend.llm.base import BaseLLMClient
from dotenv import load_dotenv

class GeminiClient(BaseLLMClient):
    def __init__(self, config):
        super().__init__(config)
        self.model = genai.GenerativeModel(config.model_name)

    def complete(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
            }
        )
        return response.text
