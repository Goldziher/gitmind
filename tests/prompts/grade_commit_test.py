import pytest

from gitmind.exceptions import LLMClientError
from gitmind.llm.base import RetryConfig
from gitmind.prompts import GradeCommitHandler
from gitmind.prompts.grade_commit import CommitGradingResult
from gitmind.rules import DEFAULT_GRADING_RULES
from gitmind.utils.commit import CommitMetadata, CommitStatistics
from tests.data_fixtures import grade_commit_response
from tests.helpers import create_mock_client


async def test_grade_commit_success_path(commit_data: tuple[CommitStatistics, CommitMetadata, str]) -> None:
    mock_client = create_mock_client(return_value=grade_commit_response)
    _, metadata, diff = commit_data

    handler = GradeCommitHandler(mock_client)
    results = await handler(metadata=metadata, diff=diff, grading_rules=DEFAULT_GRADING_RULES)

    expected_results = {
        k: CommitGradingResult(grade=item["grade"], reason=item["reason"])
        for k, item in dict(sorted(results.items())).items()
    }

    assert results == expected_results


async def test_grade_commit_failure_path_client_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(exc=LLMClientError("test"))
    _, metadata, diff = commit_data

    handler = GradeCommitHandler(mock_client)

    with pytest.raises(LLMClientError):
        await handler(metadata=metadata, diff=diff, grading_rules=DEFAULT_GRADING_RULES)

    assert mock_client.create_completions.call_count == 1


async def test_grade_commit_failure_path_validation_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(return_value='{"key": value}')
    _, metadata, diff = commit_data

    handler = GradeCommitHandler(mock_client, retry_config=RetryConfig(max_retries=1))

    with pytest.raises(LLMClientError):
        await handler(metadata=metadata, diff=diff, grading_rules=DEFAULT_GRADING_RULES)

    assert mock_client.create_completions.call_count == 2


async def test_grade_commit_failure_path_decode_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(return_value='{"key": val')
    _, metadata, diff = commit_data

    handler = GradeCommitHandler(mock_client, retry_config=RetryConfig(max_retries=1))

    with pytest.raises(LLMClientError):
        await handler(metadata=metadata, diff=diff, grading_rules=DEFAULT_GRADING_RULES)

    assert mock_client.create_completions.call_count == 2
