from logging import Logger
from os import environ
from pathlib import Path

import pytest
from pygit2 import Repository

from gitmind.llm.base import LLMClient
from gitmind.prompts import GradeCommitHandler
from gitmind.utils.commit import extract_commit_data, get_commit
from gitmind.utils.serialization import serialize
from tests.e2e.conftest import TEST_COMMIT_HASH


@pytest.mark.skipif(
    not environ.get("E2E_TESTS"),
    reason="End-to-end tests are disabled. Set E2E_TESTS to execute the E2E tests",
)
async def test_describe_commit(logger: Logger, provider_name: str, provider_model: str, llm_client: LLMClient) -> None:
    """Test the describe_commit_contents function.

    Notes:
        - This test is an end-to-end test that grades a commit using the LLM client and actual network communications.
        - To execute this test ensure that all the required ENV variables are set (see conftest.py in this folder).
        - TODO: Update this E2E test to run model based evaluation.
    """
    logger.info("Initializing describe commit E2E test")

    repo = Repository(str(Path(__file__).parent.parent.parent.resolve()))
    logger.info("Found repository %s", repo.path)

    test_commit = get_commit(repo=repo, commit_hex=TEST_COMMIT_HASH)
    logger.info("Found test commit %s", str(test_commit.id))

    _, metadata, diff = extract_commit_data(commit_hex=TEST_COMMIT_HASH, repo=repo)
    logger.info("Extracted commit data for %s", str(test_commit.id))

    grading = await GradeCommitHandler(llm_client)(metadata=metadata, diff=diff)
    logger.info("Successfully graded commit %s, writing results", str(test_commit.id))

    file = Path(__file__).parent.joinpath(f".results/{provider_name}_{provider_model}_grading_{TEST_COMMIT_HASH}.json")
    file.write_bytes(serialize(grading))
    logger.info("Results written to %s", file.name)