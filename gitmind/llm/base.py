"""Base classes for LLM clients."""

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel

__all__ = ["LLMClient", "MessageDefinition", "MessageRole", "ToolDefinition", "RetryConfig"]


MessageRole = Literal["system", "user"]


class MessageDefinition(BaseModel):
    """A generic message object. An LLM client should be able to generate completions based on a list of this object."""

    role: MessageRole
    """The role of the message."""
    content: str
    """The content of the message."""


class ToolDefinition(BaseModel):
    """A tool that can be used by the LLM client to generate completions."""

    name: str
    """The name of the tool."""
    description: str | None = None
    """A description of the tool."""
    parameters: dict[str, Any]
    """The parameters the tool accepts."""


class RetryConfig(BaseModel):
    """Configuration for request retries."""

    max_retries: int = 3
    """The maximum number of retries for a request."""
    exponential_backoff: bool = True
    """Whether to use exponential backoff for retries."""


class LLMClient(ABC):
    """Base class for LLM clients.

    Args:
            api_key: The API key for the provider.
            model_name: The model to use for completions.
            endpoint_url: The endpoint URL for the provider.
            **kwargs: Additional keyword arguments.
    """

    @abstractmethod
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        endpoint_url: str | None = None,
        **kwargs: Any,
    ) -> None:  # pragma: no cover
        ...

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
        ...
