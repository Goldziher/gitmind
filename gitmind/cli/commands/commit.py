from click import option
from rich_click import Context, echo, group, pass_context

from gitmind.cli._utils import get_or_set_cli_context
from gitmind.utils.commit import get_commit
from gitmind.utils.sync import run_as_sync


@group()
def commit() -> None:
    """Commit commands."""


@commit.command()
@option("--commit-hash", required=True, type=str)
@pass_context
@run_as_sync
async def grade(ctx: Context, commit_hash: str) -> None:
    """Grade a commit."""
    cli_ctx = get_or_set_cli_context(ctx)
    cli_ctx["commit_hash"] = commit_hash
    commit = get_commit(repo=cli_ctx["repo"], commit_hex=commit_hash)
    echo(f"Commit {commit_hash}: {commit.message}")


@commit.command()
@option("--commit-hash", required=True, type=str)
@pass_context
@run_as_sync
async def describe(ctx: Context, commit_hash: str) -> None:
    """Describe a commit."""
    cli_ctx = get_or_set_cli_context(ctx)
    cli_ctx["commit_hash"] = commit_hash
    commit = get_commit(repo=cli_ctx["repo"], commit_hex=commit_hash)
    echo(f"Commit {commit_hash}: {commit.message}")
