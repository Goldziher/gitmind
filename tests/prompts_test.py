import pytest

from exceptions import LLMClientError
from src.data_types import CommitDataDTO
from src.prompts import describe_commit_contents
from tests.utils import create_mock_client


async def test_describe_commit_contents_success_path(commit_data: CommitDataDTO) -> None:
    mock_client = create_mock_client(return_value="test")

    description = await describe_commit_contents(client=mock_client, commit_data=commit_data)
    assert description == "test"


async def test_describe_commit_contents_failure_path(commit_data: CommitDataDTO) -> None:
    mock_client = create_mock_client(exc=LLMClientError("test"))

    with pytest.raises(LLMClientError):
        await describe_commit_contents(client=mock_client, commit_data=commit_data)
