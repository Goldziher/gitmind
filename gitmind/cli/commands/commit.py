from click import option
from rich_click import Context, argument, echo, group, pass_context

from gitmind.utils.sync import run_as_sync


@group()
def commit() -> None:
    pass


@commit.command()
@option("--commit-hash", required=True, type=str)
@pass_context
@run_as_sync
async def grade(ctx: Context, commit_hash: str) -> None:
    echo(f"Commit {commit_hash}")


@commit.command()
@argument("commit_hash", required=True, type=str)
@pass_context
@run_as_sync
async def describe(ctx: Context, commit_hash: str) -> None:
    """Describe a commit."""
    echo(f"Commit {commit_hash}")
    # try:
    #     settings = get_settings_from_context(ctx)
    #     repo = get_repo(getcwd())
    #     commit = get_commit(repo=repo, hexsha=commit_hash)
    #     echo(settings.model_dump_json())
    #     echo(f"Commit {commit_hash}: {commit.message}")
    # except BadName as e:
    #     raise UsageError(f"Invalid commit hash: {commit_hash}", ctx=ctx) from e
