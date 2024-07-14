from rich_click import group, rich_click

from gitmind.cli._utils import global_options
from gitmind.cli.commands import commit

rich_click.USE_RICH_MARKUP = True
rich_click.SHOW_ARGUMENTS = True
rich_click.GROUP_ARGUMENTS_OPTIONS = True
rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
rich_click.SHOW_METAVARS_COLUMN = True
rich_click.APPEND_METAVARS_HELP = True


@group()  # type: ignore[arg-type]
@global_options()
def cli() -> None:
    """GitMind CLI."""


cli.add_command(commit)
