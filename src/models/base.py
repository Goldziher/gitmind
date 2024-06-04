from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from pydantic import BaseModel

type ModelConfig[T: BaseModel] = T


class AIModel[ModelConfig](ABC):
    """ABC for AI model wrappers.

    The class provides a common interface for interacting with different AI models.
    """

    config: ModelConfig

    def __init__(self, config: ModelConfig) -> None:
        """Initialize the AI model with the provided configuration."""
        self.config = config

    @abstractmethod
    async def stream_prompt(self, prompt_content: str) -> AsyncIterator[str]:
        """Send a prompt to the model and stream the response content asynchronously."""
        raise NotImplementedError

    @abstractmethod
    async def prompt(self, prompt_content: str) -> str:
        """Send a prompt to the model and return the response content."""
        raise NotImplementedError
