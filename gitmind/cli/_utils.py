from collections.abc import Callable
from pathlib import Path
from typing import (  # type: ignore[attr-defined]
    Any,
    NotRequired,
    ParamSpec,
    TypedDict,
    TypeVar,
    _LiteralGenericAlias,
    cast,
)

from pydantic import ValidationError
from pygit2 import Repository
from rich_click import Choice, Context, UsageError, option

from gitmind.config import GitMindSettings
from gitmind.utils.repository import get_or_clone_repository

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
            # since we use a pydantic validator to ensure this value is not actually None, this cast is safe
            target_repo = cast(Path | str, settings.target_repo)
            ctx.obj = CLIContext(settings=settings, repo=get_or_clone_repository(target_repo))

        return cast(CLIContext, ctx.obj)
    except ValidationError as e:
        field_names = "\n".join([f"-\t{value["loc"][0]}" for value in e.errors()])
        raise UsageError(
            f"Invalid configuration settings. The following options are required:\n\n{field_names}",
        ) from e


def global_options() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Global CLI options.

    Notes:
        - this decorator is used to add global options to root group

    Returns:
        The decorator.
    """
    options: list[Callable[[Callable[P, T]], Callable[P, T]]] = []

    for field_name, field_info in sorted(GitMindSettings.model_fields.items()):
        option_param = f"--{field_name.replace("_", "-")}"
        if isinstance(field_info.annotation, _LiteralGenericAlias):
            # we have a generic type and all its args are strings, we can assume this is a Literal - so we can trust that args are choice values
            option_type: Choice | type = Choice(list(field_info.annotation.__args__))
        elif any(field_info.annotation is t for t in (str, int, float, bool)):
            option_type = cast(type, field_info.annotation)
        else:
            option_type = str

        options.append(
            option(
                option_param,
                help=field_info.description,
                type=option_type,
                required=False,
            )
        )

        def wrapper(fn: Callable[P, T]) -> Callable[P, T]:
            for opt in reversed(options):
                fn = opt(fn)
            return fn

    return wrapper


if __name__ == "__main__":
    global_options()
