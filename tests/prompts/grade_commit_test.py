import pytest

from git_critic.configuration_types import RetryConfig
from git_critic.data_types import CommitGradingResult, CommitMetadata, CommitStatistics
from git_critic.exceptions import LLMClientError
from git_critic.prompts import GradeCommitHandler
from git_critic.rules import DEFAULT_GRADING_RULES
from tests.data_fixtures import grade_commit_response
from tests.utils import create_mock_client


async def test_grade_commit_success_path(commit_data: tuple[CommitStatistics, CommitMetadata, str]) -> None:
    mock_client = create_mock_client(return_value=grade_commit_response)
    _, metadata, diff = commit_data

    handler = GradeCommitHandler(mock_client)
    results = await handler(metadata=metadata, diff=diff, grading_rules=DEFAULT_GRADING_RULES)

    expected_results = [
        CommitGradingResult(
            rule_name="coding_standards",
            grade=8,
            reason="The commit predominantly adheres to coding standards. However, there are some minor issues, such as removing sensitive information, which could have been handled more securely.",
        ),
        CommitGradingResult(
            rule_name="commit_atomicity",
            grade=9,
            reason="The commit captures a single logical change focused on updating and refining multiple files. There is a consistent theme of refactoring, cleanup, and dependency updates.",
        ),
        CommitGradingResult(
            rule_name="code_quality",
            grade=8,
            reason="The code changes are well-implemented and follow best practices. There was a significant effort in refining method signatures and improving error handling. No signs of new bugs or issues introduced.",
        ),
        CommitGradingResult(
            rule_name="message_quality",
            grade=9,
            reason="The commit message provides a comprehensive breakdown of the changes made. It's detailed, descriptive, and reflects the nature and intention of the commit accurately.",
        ),
        CommitGradingResult(
            rule_name="documentation_quality",
            grade=8,
            reason="The documentation in `git_critic/llm/result.md` is comprehensive and clear. However, some of the refactored code could benefit from additional inline comments for better clarity.",
        ),
        CommitGradingResult(
            rule_name="codebase_impact",
            grade=8,
            reason="The changes enhance the overall quality, security, and consistency of the codebase. Removing hardcoded credentials is particularly impactful, although this could have been managed more securely. No net additions or deletions in functionality keep the impact moderate.",
        ),
        CommitGradingResult(
            rule_name="changes_scope",
            grade=8,
            reason="The scope of changes is appropriate and cohesive, covering various related aspects such as dependencies, method signatures, and cleanup. It ensures thorough consistency but might be slightly broad for one commit.",
        ),
        CommitGradingResult(
            rule_name="test_quality",
            grade=1,
            reason="No new tests were added, and an entire test file was removed. While the changes are refactorings, it's crucial to have tests that validate such substantial changes.",
        ),
        CommitGradingResult(
            rule_name="triviality",
            grade=8,
            reason="The changes are significant and contribute to improving the codebase. They cover essential aspects such as removing hardcoded secrets, updating dependencies, and refactoring method signatures.",
        ),
    ]

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
