from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from git.types import Files_TD, PathLike


class CommitMetadata(TypedDict):
    """DTO for commit descriptors."""

    commit_author_email: str | None
    """The email of the author of the commit."""
    commit_author_name: str | None
    """The name of the author of the commit."""
    commit_authored_timestamp: int
    """The unix UTC timestamp of when commit was authored."""
    commit_commited_timestamp: int
    """The unix UTC timestamp of when the commit was committed."""
    commit_commiter_email: str | None
    """The email of the committer of the commit."""
    commit_commiter_name: str | None
    """The name of the committer of the commit."""
    commit_hash: str
    """The hash of the commit."""
    commit_message: str
    """The message of the commit."""


class CommitStatistics(TypedDict):
    """DTO for commit data."""

    num_additions: int
    """The number of additions in the commit."""
    num_copies: int
    """The number of copies in the commit."""
    num_deletions: int
    """The number of deletions in the commit."""
    num_modifications: int
    """The number of modifications in the commit."""
    num_renames: int
    """The number of renames in the commit."""
    num_type_changes: int
    """The number of type changes in the commit."""
    num_unmerged: int
    """The number of unmerged changes in the commit."""
    parent_commit_hash: str | None
    """The hash of the parent commit."""
    per_files_changes: dict["PathLike", "Files_TD"]
    """The changes per file in the commit."""
    total_files_changed: int
    """The total number of files changed in the commit."""
    total_lines_changed: int
    """The total number of lines changed in the commit."""


class CommitFileChangeDescription(TypedDict):
    """Description of the changes made in a file in a commit."""

    file_name: str
    """The name of the file."""
    changes_description: str
    """Description of the changes made in the file and their purpose."""


class CommitDescriptionResult(TypedDict):
    """Description of a commit."""

    summary: str
    """Summary of the commit."""
    purpose: str
    """An estimation to the purpose of the changes made in the commit and it's relative impact."""
    breakdown: list[CommitFileChangeDescription]
    """Description of changes in each file and the purpose of the changes."""
    programming_languages_used: list[str]
    """List of programming languages used in the commit."""
    additional_notes: str
    """Any additional relevant information."""


class CommitGradingResult(TypedDict):
    """DTO for grading results."""

    grade: int
    """The grade for the commit."""
    reason: str
    """The reason for the grade."""
    rule_name: str
    """The name of the rule."""


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
