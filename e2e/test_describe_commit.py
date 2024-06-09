import asyncio
from datetime import UTC, datetime
from logging import Logger
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from src.commit import extract_commit_data
from src.llm.groq_client import GroqClient, GroqOptions
from src.llm.openai_client import OpenAIClient, OpenAIOptions
from src.prompts import describe_commit_contents
from src.repository import get_commits
from src.utils.logger import get_logger

if TYPE_CHECKING:
    from src.llm.base import LLMClient


async def test_describe_commit(logger: Logger) -> None:
    """Test the describe_commit_contents function."""
    provider = environ.get("PROVIDER")
    assert provider is not None, "PROVIDER is not set"

    match provider.lower():
        case "openai":
            openai_key = environ.get("OPENAI_API_KEY")
            assert openai_key is not None, "OPENAI_API_KEY is not set"

            model: str = "gpt-4o"
            client: LLMClient = OpenAIClient(
                options=OpenAIOptions(
                    api_key=openai_key,
                    model=model,
                )
            )
        case "groq":
            groq_key = environ.get("GROQ_API_KEY")
            assert groq_key is not None, "GROQ_API_KEY is not set"

            model = "llama3-70b-8192"
            client = GroqClient(
                options=GroqOptions(
                    api_key=groq_key,
                    model=model,
                )
            )
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")

    commits = get_commits(Path(__file__).parent.parent.resolve())

    for commit in [c for c in commits if c.hexsha == "9c8399e0fe619ff66f8bebe64039fc23a7f107cd"]:
        commit_data, diff_contents = extract_commit_data(commit)
        description = await describe_commit_contents(
            client=client, commit_data=commit_data, diff_contents=diff_contents
        )

        logger.info("Description for commit %s: %s", commit.hexsha, description)

        Path(__file__).parent.joinpath(
            f".results/{provider}_{model}_describe_{commit.hexsha}_{datetime.now(UTC)}.md"
        ).write_text(description)


if __name__ == "__main__":
    environ.setdefault("DEBUG_LOGGING", "true")
    logger = get_logger(__name__)

    load_dotenv()
    logger.info("Running test_describe_commit")

    asyncio.run(test_describe_commit(logger))
