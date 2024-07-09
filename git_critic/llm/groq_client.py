import logging
from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Any

from groq import DEFAULT_MAX_RETRIES, NOT_GIVEN, GroqError, NotGiven
from groq.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from groq.types.chat.completion_create_params import ResponseFormat
from groq.types.shared_params import FunctionDefinition
from pydantic import BaseModel, ConfigDict
from tree_sitter_language_pack import SupportedLanguage, get_binding

from git_critic.configuration_types import MessageDefinition, MessageRole, ToolDefinition
from git_critic.exceptions import EmptyContentError, LLMClientError
from git_critic.llm.base import LLMClient
from git_critic.utils.chunking import ChunkingType, get_chunker

if TYPE_CHECKING:
    from groq import AsyncClient

logger = logging.getLogger(__name__)

_groq_message_mapping: dict[MessageRole, type[ChatCompletionMessageParam]] = {
    "system": ChatCompletionSystemMessageParam,
    "user": ChatCompletionUserMessageParam,
}


class GroqOptions(BaseModel):
    """Base options for Groq clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    """The API key for the Groq model."""
    base_url: str | None = None
    """The base URL for the Groq model."""
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
        messages: list[MessageDefinition],
        json_response: bool = False,
        tool: ToolDefinition | None = None,
        **kwargs: Any,
    ) -> str:
        """Create completions.

        Args:
            messages: The messages to generate completions for.
            json_response: Whether to return the response as a JSON object.
            tool: An optional tool call.
            **kwargs: Additional completion options.

        Raises:
            LLMClientError: If an error occurs while creating completions.

        Returns:
            The completion generated by the client.
        """
        try:
            result = await self._client.chat.completions.create(  # type: ignore[call-overload]
                model=self._model,
                messages=[
                    _groq_message_mapping[message.role](role=message.role, content=message.content)  # type: ignore
                    for message in messages
                ],
                response_format=ResponseFormat(type="json_object" if json_response else "text"),
                stream=not tool,
                tools=[
                    ChatCompletionToolParam(
                        type="function",
                        function=FunctionDefinition(
                            name=tool.name,
                            parameters=tool.parameters,
                            description=tool.description or "",
                        ),
                    )
                ]
                if tool is not None
                else NOT_GIVEN,
                tool_choice="auto" if tool else NOT_GIVEN,
                **kwargs,
            )
        except GroqError as e:
            raise LLMClientError("Failed to generate completion", context=str(e)) from e

        if content := result.choices[0].message.tool_calls[0].function.arguments:
            return content

        raise EmptyContentError("LLM client returned empty content", context=result.model_dump_json())

    def chunk_content(
        self, content: str, max_tokens: int, chunking_type: ChunkingType, language: SupportedLanguage | None = None
    ) -> Generator[str, None, None]:
        """Chunk the given content into chunks of the given size.

        Args:
            content: The content to chunk.
            max_tokens: The maximum number of tokens per chunk.
            chunking_type: The type of content to chunk.
            language: The language to use for code chunking.

        Returns:
            A list of chunks.
        """
        kwargs = {"model": "gpt-3.5-turbo", "capacity": max_tokens}
        if language:
            kwargs["language"] = get_binding(language)

        chunker = get_chunker(chunking_type).from_tiktoken_model(**kwargs)
        yield from chunker.chunks(content)
