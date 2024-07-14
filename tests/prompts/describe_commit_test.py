import pytest

from gitmind.exceptions import LLMClientError
from gitmind.llm.base import RetryConfig
from gitmind.prompts import DescribeCommitHandler
from gitmind.prompts.describe_commit import CommitDescriptionResult
from gitmind.utils.commit import CommitMetadata, CommitStatistics
from gitmind.utils.serialization import deserialize
from tests.data_fixtures import describe_commit_response
from tests.helpers import create_mock_client


async def test_describe_commit_contents_success_path(commit_data: tuple[CommitStatistics, CommitMetadata, str]) -> None:
    mock_client = create_mock_client(return_value=describe_commit_response)

    statistics, metadata, diff_content = commit_data
    description = await DescribeCommitHandler(mock_client)(statistics=statistics, diff=diff_content, metadata=metadata)
    assert description == deserialize(describe_commit_response, CommitDescriptionResult)


async def test_describe_commit_contents_failure_path_client_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(exc=LLMClientError("test"))

    statistics, metadata, diff_content = commit_data

    with pytest.raises(LLMClientError):
        await DescribeCommitHandler(mock_client)(
            statistics=statistics, diff=diff_content, metadata=metadata, retry_config=RetryConfig(max_retries=1)
        )

    assert mock_client.create_completions.call_count == 1


async def test_describe_commit_contents_failure_path_validation_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(return_value='{"key": value}')

    statistics, metadata, diff_content = commit_data

    with pytest.raises(LLMClientError):
        await DescribeCommitHandler(client=mock_client, retry_config=RetryConfig(max_retries=1))(
            statistics=statistics, diff=diff_content, metadata=metadata
        )

    assert mock_client.create_completions.call_count == 2


async def test_describe_commit_contents_failure_path_decode_error(
    commit_data: tuple[CommitStatistics, CommitMetadata, str],
) -> None:
    mock_client = create_mock_client(return_value='{"key": val')

    statistics, metadata, diff_content = commit_data

    with pytest.raises(LLMClientError):
        await DescribeCommitHandler(client=mock_client, retry_config=RetryConfig(max_retries=1))(
            statistics=statistics, diff=diff_content, metadata=metadata
        )

    assert mock_client.create_completions.call_count == 2
