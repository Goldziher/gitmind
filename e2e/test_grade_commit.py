import asyncio
from logging import Logger
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from prompts import grade_commit
from src.commit import extract_commit_data
from src.llm.groq_client import GroqClient, GroqOptions
from src.llm.openai_client import OpenAIClient, OpenAIOptions
from src.repository import get_commits
from src.utils.logger import get_logger
from utils.serialization import serialize

if TYPE_CHECKING:
    from llm.base import LLMClient


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
        commit_data = extract_commit_data(commit)

        description = (
            Path(__file__).parent.joinpath(f".results/{provider}_{model}_describe_{commit.hexsha}.md").read_text()
        )
        grading = await grade_commit(client=client, commit_data=commit_data, commit_description=description)
        logger.info("Graded commit %s", commit.hexsha)

        Path(__file__).parent.joinpath(f".results/{provider}_{model}_grading_{commit.hexsha}.json").write_bytes(
            serialize(grading)
        )


if __name__ == "__main__":
    environ.setdefault("DEBUG_LOGGING", "true")
    logger = get_logger(__name__)

    load_dotenv()
    logger.info("Running test_describe_commit")

    asyncio.run(test_describe_commit(logger))
