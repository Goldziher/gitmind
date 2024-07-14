from collections.abc import Callable
from typing import Any, NotRequired, ParamSpec, TypedDict, TypeVar, _LiteralGenericAlias, cast

from click import Choice
from pygit2 import Repository
from rich_click import Context, option

from gitmind.config import GitMindSettings

T = TypeVar("T")
P = ParamSpec("P")


class CLIContext(TypedDict):
    """The CLI context. This dict is set on the cli 'ctx.obj' attribute."""

    settings: GitMindSettings
    """The gitmind settings instance."""
    repo: Repository
    """The repository object."""
    commit_hex: NotRequired[str]
    """The commit hash."""


def get_or_set_cli_context(ctx: Context, **kwargs: Any) -> CLIContext:
    """Get settings from context.

    Args:
        ctx (Context): The context.


    Returns:
        GitMindSettings: The settings
    """
    return cast(CLIContext, ctx.obj)


def global_options() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Global CLI options.

    Notes:
        - this decorator is used to add global options to root group

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: The decorator.
    """
    options: list[Callable[[Callable[P, T]], Callable[P, T]]] = []

    for field_name, field_info in sorted(GitMindSettings.model_fields.items()):
        option_param = f"--{field_name.replace("_", "-")}"
        if isinstance(field_info.annotation, _LiteralGenericAlias):
            # we have a generic type and all its args are strings, we can assume this is a Literal - so we can trust that args are choice values
            option_type: Choice | type = Choice(list(field_info.annotation.__args__))
        elif any(field_info.annotation is t for t in (str, int, float, bool)):
            option_type = field_info.annotation
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
