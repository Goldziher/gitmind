from typing import Any, TypedDict

from pygit2 import Repository

from gitmind.llm.base import LLMClient
from gitmind.prompts.describe_commit import CommitDescriptionResult, DescribeCommitHandler
from gitmind.prompts.grade_commit import CommitGradingResult, GradeCommitHandler
from gitmind.utils.commit import CommitMetadata, CommitStatistics, extract_commit_data


class CommitData(TypedDict):
    """DTO for commit data and grading."""

    description: CommitDescriptionResult
    """The description of the commit."""
    grading: list[CommitGradingResult]
    """The grading results for the commit."""
    metadata: CommitMetadata
    """The metadata of the commit."""
    statistics: CommitStatistics
    """The data of the commit."""


async def parse_commit_contents(repo: Repository, commit_hex: str, client: LLMClient[Any]) -> CommitData:
    """Describe the contents of a commit.

    Args:
        repo: The repository object.
        commit_hex: The SHA hex of the commit to parse.
        client: The LLM client.

    Returns:
        CommitData: Parsed commit data ready for storage and consumption.
    """
    statistics, metadata, diff_contents = extract_commit_data(repo=repo, commit_hex=commit_hex)
    commit_description = await DescribeCommitHandler(client)(
        statistics=statistics, client=client, diff=diff_contents, metadata=metadata
    )
    commit_grading = await GradeCommitHandler(client)(diff=diff_contents, metadata=metadata)
    return CommitData(
        statistics=statistics,
        metadata=metadata,
        description=commit_description,
        grading=commit_grading,
    )
