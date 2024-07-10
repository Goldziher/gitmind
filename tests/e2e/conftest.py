from logging import Logger, getLogger
from os import environ
from typing import Any

import pytest

from gitmind.llm.base import LLMClient
from gitmind.llm.groq_client import GroqClient, GroqOptions
from gitmind.llm.openai_client import OpenAIClient, OpenAIOptions

TEST_COMMIT_HASH = "9c8399e0fe619ff66f8bebe64039fc23a7f107cd"


def pytest_logger_config(logger_config: Any) -> None:
    logger_config.add_loggers(["e2e"], stdout_level="info")
    logger_config.set_log_option_default("e2e")


@pytest.fixture(scope="session")
def logger() -> Logger:
    return getLogger("e2e")


@pytest.fixture(scope="session")
def provider() -> str:
    provider = environ.get("PROVIDER")
    assert provider is not None, "PROVIDER environment variable is not set"

    return provider.lower()


@pytest.fixture(scope="session")
def model() -> str:
    model = environ.get("MODEL")
    assert model is not None, "MODEL environment variable is not set"

    return model


@pytest.fixture(scope="session")
def llm_client(provider: str) -> LLMClient[Any]:
    match provider:
        case "openai":
            openai_key = environ.get("OPENAI_API_KEY")
            assert openai_key is not None, "OPENAI_API_KEY is not set"

            return OpenAIClient(
                options=OpenAIOptions(
                    api_key=openai_key,
                    model="gpt-4o",
                )
            )
        case "groq":
            groq_key = environ.get("GROQ_API_KEY")
            assert groq_key is not None, "GROQ_API_KEY is not set"

            return GroqClient(
                options=GroqOptions(
                    api_key=groq_key,
                    model="llama3-70b-8192",
                )
            )
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")
