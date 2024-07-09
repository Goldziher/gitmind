from typing import Any, Literal

from pydantic import BaseModel

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
