from collections import defaultdict
from typing import TYPE_CHECKING, Any

from git import Commit
from magic import Magic

from gitmind.data_types import CommitData, CommitMetadata, CommitStatistics
from gitmind.llm.base import LLMClient
from gitmind.prompts import DescribeCommitHandler, GradeCommitHandler

text_mime_types = {"text", "application/json", "application/xml", "application/javascript"}
mime = Magic(mime=True)

if TYPE_CHECKING:
    from git.diff import Lit_change_type


def is_supported_mime_type(mime_type: str) -> bool:
    """Check if a MIME type is supported for parsing.

    Args:
        mime_type: The MIME type to check.

    Returns:
        True if the MIME type is supported, False otherwise.
    """
    return any(mime_type.startswith(mime_type_prefix) for mime_type_prefix in text_mime_types)


def extract_commit_data(commit: Commit) -> tuple[CommitStatistics, CommitMetadata, str]:
    """Extract information from a commit.

    Notes:
        - Although GitPython provides a `stats` attribute for commits, it is insufficient for our purposes. We therefore
            calculate the statistics ourselves.

    Args:
        commit: The GitPython commit object.

    Returns:
        A tuple containing the commit statistics, metadata, and parsed diff contents.
    """
    parent_commit = commit.parents[0] if commit.parents else None
    changes = commit.diff(parent_commit, create_patch=True)
    counters: dict[Lit_change_type, int] = defaultdict(int)

    diff_list: list[str] = []
    for change in changes:
        if change.change_type:
            counters[change.change_type] += 1
        if change.diff:
            diff_list.append(change.diff.decode(errors="ignore"))

    diff_contents = "\n".join(diff_list)
    commit_message = (
        commit.message if isinstance(commit.message, str) else commit.message.decode(commit.encoding, "ignore")
    ).strip()

    statistics = CommitStatistics(
        num_additions=counters["A"],
        num_copies=counters["C"],
        num_deletions=counters["D"],
        num_modifications=counters["M"],
        num_renames=counters["R"],
        num_type_changes=counters["T"],
        num_unmerged=counters["U"],
        parent_commit_hash=parent_commit.hexsha if parent_commit else None,
        per_files_changes=dict(commit.stats.files),
        total_files_changed=len(diff_list),
        total_lines_changed=sum(len(diff.splitlines()) for diff in diff_list),
    )

    metadata = CommitMetadata(
        commit_author_email=commit.author.email,
        commit_author_name=commit.author.name,
        commit_authored_timestamp=int(commit.authored_datetime.timestamp()),
        commit_commited_timestamp=int(commit.committed_datetime.timestamp()),
        commit_commiter_email=commit.committer.email,
        commit_commiter_name=commit.committer.name,
        commit_hash=commit.hexsha,
        commit_message=commit_message,
    )

    return statistics, metadata, diff_contents


async def parse_commit_contents(commit: Commit, client: LLMClient[Any]) -> CommitData:
    """Describe the contents of a commit.

    Args:
        commit: A GitPython commit object.
        client: An LLMClient subclass instance to use.

    Returns:
        CommitData: Parsed commit data ready for storage and consumption.
    """
    statistics, metadata, diff_contents = extract_commit_data(commit=commit)
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
