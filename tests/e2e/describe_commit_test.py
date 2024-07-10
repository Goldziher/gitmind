from datetime import UTC, datetime
from logging import Logger
from os import environ
from pathlib import Path
from typing import Any

import pytest

from gitmind.commit_processing.commit import extract_commit_data
from gitmind.llm.base import LLMClient
from gitmind.prompts import DescribeCommitHandler
from gitmind.repository import get_commits
from gitmind.utils.serialization import serialize
from tests.e2e.conftest import TEST_COMMIT_HASH


@pytest.mark.skipif(
    not environ.get("E2E_TESTS"),
    reason="End-to-end tests are disabled. Set E2E_TESTS to execute the E2E tests",
)
async def test_describe_commit(logger: Logger, provider: str, model: str, llm_client: LLMClient[Any]) -> None:
    """Test the describe_commit_contents prompt.

    Notes:
        - This test is an end-to-end test that describes a commit using the LLM client and actual network communications.
        - To execute this test ensure that all the required ENV variables are set (see conftest.py in this folder).
        - TODO: Update this E2E test to run model based evaluation.
    """

    logger.info("Initializing describe commit E2E test")
    commits = get_commits(Path(__file__).parent.parent.parent.resolve())
    logger.info(f"Retrieved {len} commits")

    test_commit = next(c for c in commits if c.hexsha == TEST_COMMIT_HASH)
    logger.info(f"Found test commit {test_commit.hexsha}")

    statistics, metadata, diff = extract_commit_data(test_commit)
    logger.info(f"Extracted commit data for {test_commit.hexsha}")

    commit_description = await DescribeCommitHandler(llm_client)(statistics=statistics, diff=diff, metadata=metadata)
    logger.info(f"Successfully described commit {test_commit.hexsha}, writing results")

    file = Path(__file__).parent.joinpath(
        f".results/{provider}_{model}_describe_{TEST_COMMIT_HASH}_{datetime.now(UTC)}.json"
    )
    file.write_bytes(serialize(commit_description))
    logger.info(f"Results written to {file}")
