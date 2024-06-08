import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING

from groq import DEFAULT_MAX_RETRIES, NOT_GIVEN, GroqError, NotGiven
from groq.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from groq.types.chat.completion_create_params import ResponseFormat
from pydantic import BaseModel, ConfigDict

from src.exceptions import LLMClientError
from src.llm.base import LLMClient, Message

if TYPE_CHECKING:
    from groq import AsyncClient

logger = logging.getLogger(__name__)


class GroqOptions(BaseModel):
    """Base options for Groq clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    """The API key for the Groq model."""
    base_url: str | None = None
    model: str = "llama3-8b-8192"
    """The default model to use for generating completions."""
    timeout: float | None | NotGiven = NOT_GIVEN
    """The timeout for the HTTPX client."""
    max_retries: int = DEFAULT_MAX_RETRIES
    """The maximum number of retries for the HTTPX client."""
    default_headers: Mapping[str, str] | None = None
    """The default headers to use for the HTTPX client."""
    default_query: Mapping[str, object] | None = None
    """The default query parameters to use for the HTTPX client."""


class GroqClient(LLMClient[GroqOptions]):
    """Wrapper for Groq models."""

    _client: "AsyncClient"
    """The Groq client instance."""
    _model: str
    """The model to use for generating completions."""

    __slots__ = ("_client", "_model")

    def __init__(self, *, options: GroqOptions) -> None:
        """Initialize the Groq Client.

        Args:
            options: The Groq options.
        """
        from groq import AsyncClient

        self._client = AsyncClient(
            api_key=options.api_key,
            base_url=options.base_url,
            timeout=options.timeout,
            max_retries=options.max_retries,
            default_headers=options.default_headers,
            default_query=options.default_query,
        )
        self._model = options.model

    async def create_completions(
        self,
        *,
        messages: list[Message],
        json_response: bool = False,
    ) -> str:
        """Create completions.

        Args:
            messages: The messages to generate completions for.
            json_response: Whether to return the response as a JSON object.

        Raises:
            LLMClientError: If an error occurs while creating completions.

        Returns:
            The completion generated by the client.
        """
        try:
            result = await self._client.chat.completions.create(
                model=self._model,
                messages=self._map_messages_to_openai_message_types(messages),
                response_format=ResponseFormat(type="json_object" if json_response else "text"),
                stream=True,
            )
            content = ""
            async for chunk in result:
                if delta := chunk.choices[0].delta.content:
                    logger.info("%s", delta)
                    content += delta

            if not content:
                raise LLMClientError("Failed to generate completion")

            return content
        except GroqError as e:
            raise LLMClientError("Failed to generate completion") from e

    @staticmethod
    def _map_messages_to_openai_message_types(messages: list[Message]) -> list[ChatCompletionMessageParam]:
        """Map messages to Groq message types.

        Args:
            messages: A list of messages to map to Groq message types.

        Returns:
            A list of Groq message types.
        """
        result: list[ChatCompletionMessageParam] = []
        for message in messages:
            match message["role"]:
                case "system":
                    result.append(
                        ChatCompletionSystemMessageParam(
                            role="system",
                            content=message["content"],
                        )
                    )
                case "user":
                    result.append(
                        ChatCompletionUserMessageParam(
                            role="user",
                            content=message["content"],
                        )
                    )
                case _:
                    raise ValueError(f"Unknown message role: {message['role']}")
        return result
