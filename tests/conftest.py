from pathlib import Path
from typing import cast

import pytest
from git import Commit

from commit import extract_commit_data
from data_types import CommitDataDTO
from repository import get_commits


@pytest.fixture(scope="session")
def test_commit() -> Commit:
    commits = get_commits(Path(__file__).parent.parent.resolve())
    return cast(Commit, next(c for c in commits if c.hexsha == "9c8399e0fe619ff66f8bebe64039fc23a7f107cd"))


@pytest.fixture(scope="session")
def commit_data(test_commit: Commit) -> CommitDataDTO:
    return extract_commit_data(test_commit)
