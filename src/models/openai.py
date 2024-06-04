import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from pydantic import BaseModel

from src.models.base import AIModel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from openai import AsyncClient


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI models."""

    api_key: str
    base_url: str | None = None
    model: str = "gpt-4o"


class OpenAIModel(AIModel[OpenAIConfig]):
    """Wrapper for OpenAI models."""

    _client: "AsyncClient"
    _model: str

    def __init__(self, config: OpenAIConfig):
        """Initialize the OpenAI model.

        Args:
            config: The configuration for the model.
        """
        from openai import AsyncClient

        super().__init__(config)

        self._model = config.model
        self._client = AsyncClient(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    async def stream_prompt(self, prompt_content: str) -> AsyncIterator[str]:
        """Send a prompt to the OpenAI model and stream the response asynchronously.

        Args:
            prompt_content: The content of the prompt.

        Yields:
            str: The response from the model.
        """
        response = await self._client.completions.create(
            model=self._model, prompt=prompt_content, stream=True, temperature=0.4
        )
        async for message in response:
            ret = message["choices"][0]["text"]
            logger.debug("%s\n", ret)
            yield ret

    async def prompt(self, prompt_content: str) -> str:
        """Send a prompt to the OpenAI model and return the response.

        Args:
            prompt_content: The content of the prompt.

        Returns:
            The response from the model.
        """
        response = await self._client.completions.create(model=self._model, prompt=prompt_content, temperature=0.4)
        return response["choices"][0]["text"]
