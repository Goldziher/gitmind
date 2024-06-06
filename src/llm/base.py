"""Base classes for LLM clients."""

from abc import ABC, abstractmethod
from typing import Generic, TypedDict, TypeVar

ClientConfig = TypeVar("ClientConfig")


class Message(TypedDict):
    """A generic message object. An LLM client should be able to generate completions based on a list this object."""

    role: str
    """The role of the message."""
    content: str
    """The content of the message."""


class LLMClient(ABC, Generic[ClientConfig]):
    """Base class for LLM clients."""

    @abstractmethod
    def __init__(self, *, config: ClientConfig) -> None:  # pragma: no cover
        """Initialize the client.

        Args:
            config: The client configuration.
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def create_completions(
        self, *, messages: list[Message], json_response: bool = False
    ) -> str:  # pragma: no cover
        """Create completions.

        Args:
            messages: The messages to generate completions for.
            json_response: Whether to return the response as a JSON object.

        Raises:
            LLMClientError: If an error occurs while creating completions.

        Returns:
            The completion generated by the client.
        """
        raise NotImplementedError("Method not implemented")
