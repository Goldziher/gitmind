"""Base classes for LLM clients."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Generic, Literal, TypeVar, overload

from pydantic import BaseModel
from tree_sitter import Language

from git_critic.configuration_types import MessageDefinition, ToolDefinition
from git_critic.utils.chunking import ChunkingType

T = TypeVar("T", bound=BaseModel)
M = TypeVar("M")


class LLMClient(ABC, Generic[T]):
    """Base class for LLM clients."""

    @abstractmethod
    def __init__(self, *, config: T) -> None:  # pragma: no cover
        """Initialize the client.

        Args:
            config: The client configuration.
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def create_completions(
        self,
        *,
        messages: list[MessageDefinition],
        json_response: bool = False,
        tool: ToolDefinition | None = None,
        **kwargs: Any,
    ) -> str:  # pragma: no cover
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
        raise NotImplementedError("Method not implemented")

    @overload
    def chunk_content(
        self, content: str, max_tokens: int, chunking_type: Literal["code"], language: Language
    ) -> Generator[str, None, None]: ...

    @overload
    def chunk_content(
        self, content: str, max_tokens: int, chunking_type: Literal["text", "markdown"]
    ) -> Generator[str, None, None]: ...

    @abstractmethod
    def chunk_content(
        self, content: str, max_tokens: int, chunking_type: ChunkingType, language: Language | None = None
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
        raise NotImplementedError("Method not implemented")
