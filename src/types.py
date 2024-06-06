from typing import TYPE_CHECKING, TypedDict

from git.types import PathLike

if TYPE_CHECKING:
    from git.types import Files_TD


class Rule(TypedDict):
    """A grading rule."""

    name: str
    """The name of the rule."""
    title: str
    """The title of the rule."""
    evaluation_guidelines: str
    """The description of the rule."""
    additional_conditions: list[str] | None
    """Additional conditions for the rule."""
    min_grade_description: str
    """The minimum grade for the rule."""
    max_grade_description: str
    """The maximum grade for the rule."""


class CommitDataDTO(TypedDict):
    """DTO for commit data."""

    total_files_changed: int
    """The total number of files changed in the commit."""
    total_lines_changed: int
    """The total number of lines changed in the commit."""
    per_files_changes: dict[str | PathLike, "Files_TD"]
    """The changes per file in the commit."""
    author_email: str | None
    """The email of the author of the commit."""
    author_name: str | None
    """The name of the author of the commit."""
    diff_contents: str
    """The contents of the commit."""
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


class CommitGradingResult(TypedDict):
    """DTO for grading results."""

    grade: int
    """The grade for the commit."""
    reason: str
    """The reason for the grade."""
    rule_name: str
    """The name of the rule."""


class ParsedCommitDTO(TypedDict):
    """DTO for commit data and grading."""

    commit_hash: str
    """The hash of the commit."""
    commit_data: CommitDataDTO
    """The data of the commit."""
    commit_description: str
    """The description of the commit."""
    commit_grading: list[CommitGradingResult]
    """The grading results for the commit."""
