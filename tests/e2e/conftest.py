from logging import Logger, getLogger
from os import environ
from typing import Any

import pytest

from gitmind.llm.base import LLMClient
from gitmind.llm.groq_client import GroqClient
from gitmind.llm.openai_client import OpenAIClient

TEST_COMMIT_HASH = "9c8399e0fe619ff66f8bebe64039fc23a7f107cd"


def pytest_logger_config(logger_config: Any) -> None:
    logger_config.add_loggers(["e2e"], stdout_level="info")
    logger_config.set_log_option_default("e2e")


@pytest.fixture(scope="session")
def logger() -> Logger:
    return getLogger("e2e")


@pytest.fixture(scope="session")
def provider_name() -> str:
    provider_name = environ.get("PROVIDER_NAME", None)
    assert provider_name is not None, "PROVIDER_NAME environment variable is not set"

    return provider_name


@pytest.fixture(scope="session")
def llm_client(provider_name: str) -> LLMClient:
    if provider_name == "groq":
        groq_key = environ.get("GROQ_API_KEY")
        assert groq_key is not None, "GROQ_API_KEY is not set"

        return GroqClient(
            api_key=groq_key,
            model_name="llama3-70b-8192",
        )

    openai_key = environ.get("OPENAI_API_KEY")
    assert openai_key is not None, "OPENAI_API_KEY is not set"

    return OpenAIClient(
        api_key=openai_key,
        model_name="gpt-4o",
    )
