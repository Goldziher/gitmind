from collections.abc import Callable

from pygit2 import Remote, Repository
from pygit2 import clone_repository as pygit_clone_repository
from pygit2.callbacks import RemoteCallbacks


def clone_repository(
    *,
    url: str,
    path: str,
    bare: bool = False,
    branch: str | None = None,
    callbacks: RemoteCallbacks | None = None,
    depth: int = 0,
    remote: Callable[[Repository, str, str], Remote] | None = None,
) -> Repository:
    """Clone a Git repository. This is a wrapper around pygit2.clone_repository that adds proper typing.

    Args:
        bare: Whether to clone the repository as a bare repository.
        branch: The branch to checkout.
        callbacks: The remote callbacks to use.
        depth: The depth of the clone.
        path: The path to the target directory.
        remote: The remote callback to use.
        url: The path to the Git repository.

    Returns:
        The cloned Git repository.
    """
    return pygit_clone_repository(
        bare=bare,
        callbacks=callbacks,
        checkout_branch=branch,
        depth=depth,
        path=str(path),
        remote=remote,
        url=str(url),
    )
