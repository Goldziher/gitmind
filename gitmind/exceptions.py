from typing import Any


class GitMindError(Exception):
    """Base class for all exceptions in critic."""

    def __init__(self, message: str, context: Any = None) -> None:
        super().__init__(message)
        self.context = context


class LLMClientError(GitMindError):
    """Error that occurs when an LLM client encounters an issue."""


class EmptyContentError(GitMindError):
    """Error that occurs when an LLM response content is empty."""


class MissingDependencyError(GitMindError):
    """Error that occurs when a dependency is not installed."""


class ConfigurationError(GitMindError):
    """Error that occurs when a configuration is invalid."""
