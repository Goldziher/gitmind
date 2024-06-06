import asyncio
from logging import Logger
from os import environ
from pathlib import Path

from dotenv import load_dotenv

from src.commit import extract_commit_data
from src.llm.openai_client import OpenAIClient, OpenAIOptions
from src.prompts import describe_commit_contents
from src.repository import get_commits
from src.utils.logger import get_logger


async def test_describe_commit(logger: Logger) -> None:
    """Test the describe_commit_contents function."""
    openai_key = environ.get("OPENAI_API_KEY")
    assert openai_key is not None, "OPENAI_API_KEY is not set"

    client = OpenAIClient(
        options=OpenAIOptions(
            api_key=openai_key,
            model="gpt-4o",
        )
    )

    commits = get_commits(Path(__file__).parent.parent.resolve())
    for commit in commits:
        logger.info("Describing commit %s", commit.hexsha)
        commit_data = extract_commit_data(commit)
        description = await describe_commit_contents(client=client, commit_data=commit_data)
        logger.info("Description for commit %s: %s", commit.hexsha, description)


if __name__ == "__main__":
    environ.setdefault("DEBUG_LOGGING", "true")
    logger = get_logger(__name__)

    load_dotenv()
    logger.info("Running test_describe_commit")

    asyncio.run(test_describe_commit(logger))
