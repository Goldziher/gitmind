from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Final, Generic, TypeVar

from anyio import sleep
from jsonschema import ValidationError, validate
from msgspec import DecodeError

from gitmind.configuration_types import MessageDefinition, RetryConfig, ToolDefinition
from gitmind.exceptions import LLMClientError
from gitmind.llm.base import LLMClient
from gitmind.utils.logger import get_logger
from gitmind.utils.serialization import deserialize, serialize

logger = get_logger(__name__)

T = TypeVar("T")


DEFAULT_CHUNK_SIZE: Final[int] = 128000
MAX_TOKENS: Final[int] = 4096


class AbstractPromptHandler(ABC, Generic[T]):
    """Base class for LLM prompt handlers."""

    __slots__ = ("_client", "_retry_config", "_chunk_size", "_max_response_tokens")

    def __init__(
        self,
        client: LLMClient[Any],
        retry_config: RetryConfig | None = None,
        chunk_size: int | None = None,
        max_response_tokens: int | None = None,
    ) -> None:
        """Initialize the prompt handler.

        Args:
            client: The LLM client to use.
            retry_config: The retry configuration to use.
            chunk_size: The chunk size to use when chunking prompt contexts.
            max_response_tokens: The maximum number of tokens in the response.
        """
        self._client = client
        self._retry_config = retry_config if retry_config else RetryConfig()
        self._chunk_size = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE
        self._max_response_tokens = max_response_tokens if max_response_tokens else MAX_TOKENS

    @abstractmethod
    async def __call__(self, **kwargs: Any) -> T:
        """Generate LLM completions.

        Args:
            **kwargs: Additional arguments .

        Returns:
            The completion generated by the client.
        """
        raise NotImplementedError("Method not implemented")

    async def generate_completions(
        self,
        *,
        messages: list[MessageDefinition],
        properties: dict[str, Any],
        tool: ToolDefinition | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        """Generate LLM completions.

        Args:
            messages: The messages to generate completions for.
            properties: The properties to validate.
            tool: An optional tool call.
            retry_count: The number of retries attempted.

        Returns:
            The response from the LLM client.
        """
        try:
            logger.debug(
                "%s: Generating completions.\n\nPrompt: %s", self.__class__.__name__, serialize(messages).decode()
            )
            response = await self._client.create_completions(
                messages=messages, json_response=True, tool=tool, max_tokens=self._max_response_tokens
            )
            logger.debug("%s: Successfully generated completions.\n\nResponse: %s", self.__class__.__name__, response)
            return self.parse_json_response(response=response, properties=properties)
        except LLMClientError as e:
            logger.error("%s: Error occurred while generating completions: %s.", self.__class__.__name__, e)
            raise
        except (DecodeError, ValidationError) as e:
            # This has to be in place because LLMs sometimes return invalid or partial JSON
            if retry_count < self._retry_config.max_retries:
                retry_count += 1
                logger.warning(
                    "LLM responded with an invalid or partial JSON response, retrying (%d/%d)",
                    retry_count,
                    self._retry_config.max_retries,
                )
                await sleep((2**retry_count) if self._retry_config.exponential_backoff else 1)
                return await self.generate_completions(
                    messages=messages,
                    properties=properties,
                    tool=tool,
                    retry_count=retry_count,
                )
            logger.warning("LLM responded with invalid or partial JSON response, retries have been exhausted.")
            raise LLMClientError(
                "LLM responded with invalid or partial JSON response",
                context=str(e),
            ) from e

    async def combine_results(
        self, results: list[dict[str, Any]], tool: ToolDefinition, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Combine multiple chunked results into a single result.

        Args:
            results: The results to combine.
            tool: The tool definition.
            properties: The properties to validate.

        Returns:
            The combined results.
        """
        return await self.generate_completions(
            properties=properties,
            messages=[
                MessageDefinition(
                    role="system",
                    content="You are an assistant tasked with combining the results of multiple LLM prompts into a "
                    "single unified result. The output must be a single JSON object of the same structure as "
                    "the objects in the provided data.",
                ),
                MessageDefinition(
                    role="user", content="Combine the following results: \n\n" + serialize(results).decode()
                ),
            ],
            tool=tool,
        )

    def chunk_content(self, content: str) -> Generator[str, None, None]:
        """Chunk the given content into chunks of the given size.

        Args:
            content: The content to chunk.

        Returns:
            A list of chunks.
        """
        for i in range(0, len(content), self._chunk_size):
            yield content[i : i + self._chunk_size]

    @staticmethod
    def parse_json_response(*, response: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Validate the response from the LLM client.

        Args:
            response: The response from the LLM client.
            properties: The properties to validate.

        Returns:
            The validated response.
        """
        try:
            parsed_response = {k: v for k, v in deserialize(response, dict).items() if k in properties}

            validate(
                instance=parsed_response,
                schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": properties,
                    "additionalProperties": False,
                    "required": list(properties),
                },
            )

            return parsed_response
        except ValidationError as e:
            logger.warning("%s: Response validation failed: %s", AbstractPromptHandler.__name__, e)
            raise e
