import asyncio
from logging import Logger
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from caching import FileSystemCache
from git_critic.commit import parse_commit_contents
from git_critic.llm.groq_client import GroqClient, GroqOptions
from git_critic.llm.openai_client import OpenAIClient, OpenAIOptions
from git_critic.repository import get_commits
from git_critic.utils.logger import get_logger
from git_critic.utils.serialization import serialize

if TYPE_CHECKING:
    from git_critic.llm.base import LLMClient


async def test_integration(logger: Logger) -> None:
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

    cache = FileSystemCache()

    for commit in get_commits(Path(__file__).parent.parent.resolve()):
        if not await cache.exists(commit.hexsha):
            parsed_commit = await parse_commit_contents(client=client, commit=commit)
            await cache.set(commit.hexsha, serialize(parsed_commit))

            logger.info("Processed commit %s", commit.hexsha)
        else:
            logger.info("Commit %s is cached, skipping", commit.hexsha)


if __name__ == "__main__":
    environ.setdefault("DEBUG_LOGGING", "true")
    logger = get_logger(__name__)

    load_dotenv()
    logger.info("Running test_integration")

    asyncio.run(test_integration(logger))
