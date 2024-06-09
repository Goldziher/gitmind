import pytest

from src.configuration_types import CommitGradingConfig, RequestRetryConfig
from src.data_types import CommitDataDTO
from src.exceptions import LLMClientError
from src.prompts import describe_commit_contents, grade_commit
from tests.utils import create_mock_client


async def test_describe_commit_contents_success_path(commit_data_dto: tuple[CommitDataDTO, str]) -> None:
    mock_client = create_mock_client(return_value="test")

    commit_data, diff_content = commit_data_dto
    description = await describe_commit_contents(
        client=mock_client, commit_data=commit_data, diff_contents=diff_content
    )
    assert description == "test"


async def test_describe_commit_contents_failure_path(commit_data_dto: tuple[CommitDataDTO, str]) -> None:
    mock_client = create_mock_client(exc=LLMClientError("test"))

    commit_data, diff_content = commit_data_dto

    with pytest.raises(LLMClientError):
        await describe_commit_contents(client=mock_client, commit_data=commit_data, diff_contents=diff_content)


async def test_grade_commit_success_path(
    commit_data_dto: tuple[CommitDataDTO, str], commit_description: str, commit_grading: str
) -> None:
    mock_client = create_mock_client(return_value=commit_grading)

    commit_data, _ = commit_data_dto
    grading = await grade_commit(
        client=mock_client, commit_data=commit_data, commit_description=commit_description, config=CommitGradingConfig()
    )
    assert grading == [
        {
            "rule_name": "coding_standards",
            "grade": 8,
            "reason": "The commit predominantly adheres to coding standards. However, there are some minor issues, such as removing sensitive information, which could have been handled more securely.",
        },
        {
            "rule_name": "commit_atomicity",
            "grade": 9,
            "reason": "The commit captures a single logical change focused on updating and refining multiple files. There is a consistent theme of refactoring, cleanup, and dependency updates.",
        },
        {
            "rule_name": "code_quality",
            "grade": 8,
            "reason": "The code changes are well-implemented and follow best practices. There was a significant effort in refining method signatures and improving error handling. No signs of new bugs or issues introduced.",
        },
        {
            "rule_name": "message_quality",
            "grade": 9,
            "reason": "The commit message provides a comprehensive breakdown of the changes made. It's detailed, descriptive, and reflects the nature and intention of the commit accurately.",
        },
        {
            "rule_name": "documentation_quality",
            "grade": 8,
            "reason": "The documentation in `src/llm/result.md` is comprehensive and clear. However, some of the refactored code could benefit from additional inline comments for better clarity.",
        },
        {
            "rule_name": "codebase_impact",
            "grade": 8,
            "reason": "The changes enhance the overall quality, security, and consistency of the codebase. Removing hardcoded credentials is particularly impactful, although this could have been managed more securely. No net additions or deletions in functionality keep the impact moderate.",
        },
        {
            "rule_name": "changes_scope",
            "grade": 8,
            "reason": "The scope of changes is appropriate and cohesive, covering various related aspects such as dependencies, method signatures, and cleanup. It ensures thorough consistency but might be slightly broad for one commit.",
        },
        {
            "rule_name": "test_quality",
            "grade": 1,
            "reason": "No new tests were added, and an entire test file was removed. While the changes are refactorings, it's crucial to have tests that validate such substantial changes.",
        },
        {
            "rule_name": "triviality",
            "grade": 8,
            "reason": "The changes are significant and contribute to improving the codebase. They cover essential aspects such as removing hardcoded secrets, updating dependencies, and refactoring method signatures.",
        },
    ]


async def test_grade_commit_failure_path(commit_data_dto: tuple[CommitDataDTO, str], commit_description: str) -> None:
    mock_client = create_mock_client(exc=LLMClientError("test"))
    commit_data, _ = commit_data_dto

    with pytest.raises(LLMClientError):
        await grade_commit(
            client=mock_client,
            commit_data=commit_data,
            commit_description=commit_description,
            config=CommitGradingConfig(
                retry_config=RequestRetryConfig(max_retries=0),
            ),
        )
