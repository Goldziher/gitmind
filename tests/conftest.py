from pathlib import Path

import pytest
from git import Commit

from src.commit import extract_commit_data
from src.data_types import CommitDataDTO
from src.repository import get_commits
from tests.data_fixtures import describe_commit_response, grade_commit_response


@pytest.fixture(scope="session")
def test_commit() -> Commit:
    commits = get_commits(Path(__file__).parent.parent.resolve())
    return next(c for c in commits if c.hexsha == "9c8399e0fe619ff66f8bebe64039fc23a7f107cd")


@pytest.fixture(scope="session")
def commit_data_dto(test_commit: Commit) -> tuple[CommitDataDTO, str]:
    return extract_commit_data(test_commit)


@pytest.fixture(scope="session")
def commit_description() -> str:
    return describe_commit_response


@pytest.fixture(scope="session")
def commit_grading() -> str:
    return grade_commit_response
