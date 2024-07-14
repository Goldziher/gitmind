from typing import TypedDict

from pygit2 import Commit, Repository


class CommitMetadata(TypedDict):
    """DTO for commit descriptors."""

    author_email: str | None
    """The email of the author of the commit."""
    author_name: str | None
    """The name of the author of the commit."""
    commiter_email: str | None
    """The email of the committer of the commit."""
    commiter_name: str | None
    """The name of the committer of the commit."""
    hex: str
    """The hash of the commit."""
    message: str
    """The message of the commit."""
    parent_hex: str | None
    """The hash of the parent commit."""
    timestamp: int
    """The unix UTC timestamp of when the commit was committed."""


class CommitStatistics(TypedDict):
    """DTO for commit statistics."""

    deletions: int
    """The number of deletions in the commit."""
    files_changed: int
    """The number of files changed in the commit."""
    insertions: int
    """The number of insertions in the commit."""


def get_commit(*, repo: Repository, commit_hex: str) -> Commit:
    """Get a commit object from a repository.

    Args:
        repo: The GitPython repository object.
        commit_hex: The SHA hex of the commit to retrieve.

    Raises:
        ValueError: If the object with the given SHA is not a commit.

    Returns:
        The commit object.
    """
    git_object = repo.revparse_single(commit_hex)
    if isinstance(git_object, Commit):
        return git_object
    raise ValueError(f"GIT object with SHA hex {commit_hex} is not a commit.")


def extract_commit_data(*, repo: Repository, commit_hex: str) -> tuple[CommitStatistics, CommitMetadata, str]:
    """Extract information from a commit.

    Args:
        repo: The repository object.
        commit_hex: The SHA hex of the commit to extract information from.

    Returns:
        A tuple containing the commit statistics, metadata, and parsed diff contents.
    """
    commit = get_commit(repo=repo, commit_hex=commit_hex)
    commit_message = commit.message.strip()
    parent_commit = commit.parents[0] if commit.parents else None

    diff = repo.diff(
        a=commit.tree, b=parent_commit.tree if parent_commit is not None else None, context_lines=0, interhunk_lines=0
    )

    statistics = CommitStatistics(
        insertions=diff.stats.insertions,
        deletions=diff.stats.deletions,
        files_changed=diff.stats.files_changed,
    )

    metadata = CommitMetadata(
        author_email=commit.author.email,
        author_name=commit.author.name,
        timestamp=commit.commit_time,
        commiter_email=commit.committer.email,
        commiter_name=commit.committer.name,
        hex=str(commit.id),
        parent_hex=str(parent_commit.id) if parent_commit else None,
        message=commit_message,
    )

    return statistics, metadata, diff.patch or ""
