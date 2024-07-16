from json import dumps

from click import option
from rich_click import Context, echo, group, pass_context

from gitmind.cli._utils import debug_echo, get_or_set_cli_context
from gitmind.prompts import DescribeCommitHandler
from gitmind.prompts.describe_commit import CommitDescriptionResult
from gitmind.prompts.grade_commit import CommitGradingResult, GradeCommitHandler
from gitmind.utils.commit import extract_commit_data
from gitmind.utils.sync import run_as_sync


@group()
def commit() -> None:
    """Commit commands."""


async def handle_describe(ctx: Context, commit_hash: str) -> CommitDescriptionResult:
    """Describe a commit."""
    cli_ctx = get_or_set_cli_context(ctx)
    cli_ctx["commit_hash"] = commit_hash

    commit_statistics, commit_metadata, diff = extract_commit_data(repo=cli_ctx["repo"], commit_hex=commit_hash)
    debug_echo(
        cli_ctx,
        f"Retrieved commit {commit_hash}: {commit_metadata["message"]}\n\ncommit_data: {dumps(commit_statistics, indent=2)}",
    )
    handler = DescribeCommitHandler(
        client=cli_ctx["settings"].llm_client,
    )
    description = await handler(
        statistics=commit_statistics,
        metadata=commit_metadata,
        diff=diff,
    )
    cli_ctx["commit_description"] = description
    return description


@commit.command()
@option("--commit-hash", required=True, type=str)
@pass_context
def describe(ctx: Context, commit_hash: str) -> None:
    """Describe a commit."""
    description_result = run_as_sync(handle_describe)(ctx, commit_hash)
    echo(dumps(description_result, indent=2))


async def handle_grade(ctx: Context, commit_hash: str) -> dict[str, CommitGradingResult]:
    """Grade a commit."""
    cli_ctx = get_or_set_cli_context(ctx)
    cli_ctx["commit_hash"] = commit_hash

    commit_statistics, commit_metadata, diff = extract_commit_data(repo=cli_ctx["repo"], commit_hex=commit_hash)
    debug_echo(
        cli_ctx,
        f"Retrieved commit {commit_hash}: {commit_metadata["message"]}\n\ncommit_data: {dumps(commit_statistics, indent=2)}",
    )

    handler = GradeCommitHandler(
        client=cli_ctx["settings"].llm_client,
    )

    return await handler(
        metadata=commit_metadata,
        diff=diff,
    )


@commit.command()
@option("--commit-hash", required=True, type=str)
@pass_context
def grade(ctx: Context, commit_hash: str) -> None:
    """Grade a commit."""
    grading_results = run_as_sync(handle_grade)(ctx, commit_hash)
    echo(dumps(grading_results, indent=2))
