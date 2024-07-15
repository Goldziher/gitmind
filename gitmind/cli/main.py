from typing import Any

from rich_click import Context, echo, group, pass_context, rich_click

from gitmind.cli._utils import get_or_set_cli_context, global_options
from gitmind.cli.commands import commit

rich_click.USE_RICH_MARKUP = True
rich_click.SHOW_ARGUMENTS = True
rich_click.GROUP_ARGUMENTS_OPTIONS = True
rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
rich_click.SHOW_METAVARS_COLUMN = True
rich_click.APPEND_METAVARS_HELP = True


@group()  # type: ignore[arg-type]
@global_options()
@pass_context
def cli(ctx: Context, **kwargs: Any) -> None:
    """GitMind CLI."""
    cli_ctx = get_or_set_cli_context(ctx, **kwargs)
    if cli_ctx["settings"].mode == "debug":
        echo("initialized cli context")


cli.add_command(commit)
