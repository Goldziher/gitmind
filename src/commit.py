from collections import defaultdict
from typing import TYPE_CHECKING

from git import Commit
from magic import Magic

from src.models import AIModel
from src.prompts import describe_commit_contents, grade_commit
from src.types import CommitDataDTO, ParsedCommitDTO

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


def extract_files_from_commit(commit: Commit) -> dict[str, str]:
    """Extract files from a commit.

    Args:
        commit: The GitPython commit object.

    Returns:
        The files in the commit.
    """
    files = {}
    for item in commit.tree.traverse():
        if item.type == "blob":
            file_content = item.data_stream.read()
            mime_type = mime.from_buffer(file_content)
            if is_supported_mime_type(mime_type):
                files[item.path] = file_content.decode(errors="ignore")
    return files


def extract_commit_data(commit: Commit) -> CommitDataDTO:
    """Extract statistics from a commit.

    Notes:
        - Although GitPython provides a `stats` attribute for commits, it is insufficient for our purposes. We therefore
            calculate the statistics ourselves.

    Args:
        commit: The GitPython commit object.

    Returns:
        The statistics of the commit.
    """
    parent_commit = commit.parents[0] if commit.parents else None
    changes = commit.diff(parent_commit, create_patch=True)
    counters: dict[Lit_change_type, int] = defaultdict(int)

    diff_list: list[str] = []
    for change in changes:
        if change.change_type:
            counters[change.change_type] += 1
        if contents := str(change.diff):
            diff_list.append(contents)

    return CommitDataDTO(
        total_files_changed=len(diff_list),
        total_lines_changed=sum(len(diff.splitlines()) for diff in diff_list),
        per_files_changes={change.a_path: change for change in changes},
        author_email=commit.author.email,
        author_name=commit.author.name,
        diff_contents="".join(diff_list),
        num_additions=counters["A"],
        num_copies=counters["C"],
        num_deletions=counters["D"],
        num_modifications=counters["M"],
        num_renames=counters["R"],
        num_type_changes=counters["T"],
        num_unmerged=counters["U"],
    )


async def parse_commit_contents(commit: Commit, model: AIModel) -> ParsedCommitDTO:
    """Describe the contents of a commit.

    Args:
        commit: A GitPython commit object.
        model: The AI model to use for description.

    Returns:
        The description of the commit contents.
    """
    commit_data = extract_commit_data(commit=commit)
    commit_description = await describe_commit_contents(commit_data=commit_data, model=model)
    commit_grading = await grade_commit(
        commit_description=commit_description, commit_data=commit_data, model=model, grading_rules=None
    )
    return ParsedCommitDTO(
        **commit_data,
        commit_description=commit_description,
    )
