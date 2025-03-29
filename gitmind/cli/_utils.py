from __future__ import annotations

from typing import (  # type: ignore[attr-defined]
    TYPE_CHECKING,
    Any,
    TypedDict,
    TypeVar,
    _LiteralGenericAlias,
    cast,
)

from pydantic import ValidationError
from rich_click import Choice, Context, UsageError, echo, option
from typing_extensions import NotRequired, ParamSpec

from gitmind.config import GitMindSettings
from gitmind.utils.repository import get_or_clone_repository

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pygit2 import Repository

    from gitmind.prompts.describe_commit import CommitDescriptionResult

T = TypeVar("T")
P = ParamSpec("P")


class CLIContext(TypedDict):
    """The CLI context. This dict is set on the cli 'ctx.obj' attribute."""

    settings: GitMindSettings
    """The gitmind settings instance."""
    repo: Repository
    """The repository object."""
    commit_hash: NotRequired[str]
    """The commit hash."""
    commit_description: NotRequired[CommitDescriptionResult]
    """The commit description result, if any."""


def get_or_set_cli_context(ctx: Context, **kwargs: Any) -> CLIContext:
    """Get settings from context.

    Args:
        ctx: The click context.
        **kwargs: The keyword

    Raises:
        UsageError: If the settings are invalid.

    Returns:
        GitMindSettings: The settings
    """
    try:
        if ctx.obj is None:
            settings = GitMindSettings(**{k: v for k, v in kwargs.items() if v is not None})

            target_repo = cast("Path | str", settings.target_repo)
            ctx.obj = CLIContext(settings=settings, repo=get_or_clone_repository(target_repo))
        return cast("CLIContext", ctx.obj)
    except ValidationError as e:
        field_names = "\n".join([f"-\t{value['loc'][0]}" for value in e.errors()])
        raise UsageError(
            f"Invalid configuration settings. The following options are required:\n\n{field_names}",
        ) from e


def debug_echo(cli_context: CLIContext, message: str) -> None:
    """Echo a message if debug is enabled.

    Args:
        cli_context: The CLI context.
        message: The message to echo.
    """
    if cli_context["settings"].mode == "debug":
        echo(f"<debug>: {message}", color=True)


def get_global_option_fields() -> list[tuple[str, str, type]]:
    ret: list[tuple[str, str, type]] = []
    for field_name, field_info in sorted(GitMindSettings.model_fields.items()):
        option_param = f"--{field_name.replace('_', '-')}"
        if isinstance(field_info.annotation, _LiteralGenericAlias):
            option_type: Choice | type = Choice(list(field_info.annotation.__args__))
        elif any(field_info.annotation is t for t in (str, int, float, bool)):
            option_type = cast("type", field_info.annotation)
        else:
            option_type = str

        description = str(field_info.description) if field_info.description else ""

        if isinstance(option_type, type):
            ret.append((option_param, description, option_type))
        else:
            ret.append((option_param, description, str))
    return ret


def global_options() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Global CLI options.

    Notes:
        - this decorator is used to add global options to root group

    Returns:
        The decorator.
    """
    options: list[Callable[[Callable[P, T]], Callable[P, T]]] = [
        option(
            option_param,
            help=help_text,
            type=option_type,
            required=False,
        )
        for option_param, help_text, option_type in get_global_option_fields()
    ]

    def wrapper(fn: Callable[P, T]) -> Callable[P, T]:
        for opt in reversed(options):
            fn = opt(fn)
        return fn

    return wrapper
