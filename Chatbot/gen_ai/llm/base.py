from abc import ABC, abstractmethod
from config import ModelConfig

"""Abstract class to allow different provicers to borrow from format."""
class BaseLLMClient(ABC):
    def __init__(self, config: ModelConfig):
        self.config = config

    @abstractmethod 
    def complete(self, prompt: str) -> str:
        """Returns raw model output."""
        pass