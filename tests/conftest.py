from pathlib import Path

import pytest
from git import Commit

from git_critic.commit import extract_commit_data
from git_critic.data_types import CommitMetadata, CommitStatistics
from git_critic.repository import get_commits


@pytest.fixture(scope="session")
def test_commit() -> Commit:
    commits = get_commits(Path(__file__).parent.parent.resolve())
    return next(c for c in commits if c.hexsha == "9c8399e0fe619ff66f8bebe64039fc23a7f107cd")


@pytest.fixture(scope="session")
def commit_data(test_commit: Commit) -> tuple[CommitStatistics, CommitMetadata, str]:
    return extract_commit_data(test_commit)
