from typing import Any


class CriticError(Exception):
    """Base class for all exceptions in critic."""

    def __init__(self, message: str, context: Any = None) -> None:
        super().__init__(message)
        self.context = context


class LLMClientError(CriticError):
    """Base class for all exceptions in the LLM module."""
