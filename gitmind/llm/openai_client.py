import logging
from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Any, Union, cast

from httpx import URL
from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, NotGiven, OpenAIError
from openai.lib.azure import AsyncAzureADTokenProvider
from openai.types import ChatModel
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.shared_params import FunctionDefinition
from pydantic import BaseModel, ConfigDict
from tree_sitter_language_pack import SupportedLanguage, get_binding

from gitmind.configuration_types import MessageDefinition, MessageRole, ToolDefinition
from gitmind.exceptions import EmptyContentError, LLMClientError
from gitmind.llm.base import LLMClient
from gitmind.utils.chunking import ChunkingType, get_chunker

if TYPE_CHECKING:
    from openai import AsyncClient
    from openai.lib.azure import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

_openai_message_mapping: dict[MessageRole, type[ChatCompletionMessageParam]] = {
    "system": ChatCompletionSystemMessageParam,
    "user": ChatCompletionUserMessageParam,
}


class BaseOptions(BaseModel):
    """Base options for OpenAI clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    """The API key for the OpenAI model."""
    model: ChatModel | str = "gpt-4o"
    """The default model to use for generating completions."""
    organization: str | None = None
    """An organization namespace. Note: an error will be raised if this is not configured in the remote API."""
    project: str | None = None
    """The project namespace. Note: an error will be raised if this is not configured in the remote API"""
    timeout: float | None | NotGiven = NOT_GIVEN
    """The timeout for the HTTPX client."""
    max_retries: int = DEFAULT_MAX_RETRIES
    """The maximum number of retries for the HTTPX client."""
    default_headers: Mapping[str, str] | None = None
    """The default headers to use for the HTTPX client."""
    default_query: Mapping[str, object] | None = None
    """The default query parameters to use for the HTTPX client."""


class OpenAIOptions(BaseOptions):
    """OpenAI client options."""

    base_url: str | URL | None = None
    """The base URL for the API."""


class AzureOpenAIOptions(BaseOptions):
    """Azure OpenAI client options."""

    azure_endpoint: str
    """The Azure endpoint for the API."""
    azure_deployment: str | None = None
    """The Azure deployment for the API."""
    api_version: str | None = None
    """The API version for the Azure API."""
    azure_ad_token: str | None = None
    """The Azure AD token."""
    azure_ad_token_provider: AsyncAzureADTokenProvider | None = None
    """The Azure AD token provider."""


class OpenAIClient(LLMClient[AzureOpenAIOptions | OpenAIOptions]):
    """Wrapper for OpenAI models."""

    _client: Union["AsyncAzureOpenAI", "AsyncClient"]
    """The OpenAI client instance."""
    _model: ChatModel | str
    """The model to use for generating completions."""

    __slots__ = ("_client", "_model")

    def __init__(self, *, options: AzureOpenAIOptions | OpenAIOptions) -> None:
        """Initialize the OpenAI Client.

        Args:
            options: The OpenAI options.
        """
        if isinstance(options, AzureOpenAIOptions):
            from openai.lib.azure import AsyncAzureOpenAI

            self._client = AsyncAzureOpenAI(
                azure_endpoint=options.azure_endpoint,
                azure_deployment=options.azure_deployment,
                api_version=options.api_version,
                api_key=options.api_key,
                azure_ad_token=options.azure_ad_token,
                azure_ad_token_provider=options.azure_ad_token_provider,
                timeout=options.timeout,
                max_retries=options.max_retries,
                default_headers=options.default_headers,
                default_query=options.default_query,
            )
        else:
            from openai import AsyncClient

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
            EmptyContentError: If the LLM client returns empty content.

        Returns:
            The completion generated by the client.
        """
        try:
            result = await self._client.chat.completions.create(  # type: ignore[call-overload]
                model=self._model,
                messages=[
                    _openai_message_mapping[message.role](role=message.role, content=message.content)  # type: ignore
                    for message in messages
                ],
                response_format=ResponseFormat(type="json_object" if json_response else "text"),
                stream=False,
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
                tool_choice="required" if tool else NOT_GIVEN,
                **kwargs,
            )
        except OpenAIError as e:
            raise LLMClientError("Failed to generate completion", context=str(e)) from e

        if content := result.choices[0].message.tool_calls[0].function.arguments:
            return cast(str, content)

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
        kwargs = {"model": self._model, "capacity": max_tokens}
        if language:
            kwargs["language"] = get_binding(language)

        chunker = get_chunker(chunking_type=chunking_type, language=language, chunk_size=max_tokens, model=self._model)  # type: ignore[arg-type]
        yield from chunker.chunks(content)
