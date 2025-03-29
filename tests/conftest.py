from pathlib import Path

import pytest
from click.testing import CliRunner
from pygit2 import Commit, Repository

from gitmind.config import GitMindSettings
from gitmind.llm.base import MessageDefinition
from gitmind.utils.commit import CommitMetadata, CommitStatistics, extract_commit_data, get_commit


@pytest.fixture(scope="session")
def test_commit() -> Commit:
    repo = Repository(str(Path(__file__).parent.parent.resolve()))
    return get_commit(repo=repo, commit_hex="9c8399e0fe619ff66f8bebe64039fc23a7f107cd")


@pytest.fixture(scope="session")
def commit_data(test_commit: Commit) -> tuple[CommitStatistics, CommitMetadata, str]:
    repo = Repository(str(Path(__file__).parent.parent.resolve()))
    return extract_commit_data(repo=repo, commit_hex="9c8399e0fe619ff66f8bebe64039fc23a7f107cd")


@pytest.fixture(scope="session")
def describe_commit_message_definitions() -> list[MessageDefinition]:
    return [
        MessageDefinition(
            role="system",
            content="You are an assistant that extracts information and describes the contents of git commits.",
        ),
        MessageDefinition(
            role="user",
            content="**Commit Message**:chore: add e2e testing",
        ),
    ]


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def test_settings() -> GitMindSettings:
    return GitMindSettings(
        target_repo="https://github.com/Goldziher/gitmind",
        provider_name="openai",
        provider_api_key="abc-jeronimo",  # type: ignore[arg-type]
        provider_model="gpt-3.5-turbo",
    )
