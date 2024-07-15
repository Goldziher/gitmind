from collections.abc import Callable
from pathlib import Path

from pygit2 import Remote, Repository
from pygit2 import clone_repository as pygit_clone_repository
from pygit2.callbacks import RemoteCallbacks


def clone_repository(
    *,
    bare: bool = False,
    branch: str | None = None,
    callbacks: RemoteCallbacks | None = None,
    depth: int = 0,
    path: str,
    remote: Callable[[Repository, str, str], Remote] | None = None,
    url: str,
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


def get_or_clone_repository(target_repo: Path | str) -> Repository:
    """Get or clone a repository from a given path or url.

    Args:
        target_repo: The target repository.

    Returns:
        The repository object.
    """
    if isinstance(target_repo, Path):
        return Repository(str(target_repo))

    repo_name = target_repo.split("/")[-1]
    cache_dir = Path(".gitmind")
    cache_dir.mkdir(exist_ok=True, parents=True)

    repositories_dir = cache_dir.joinpath("repositories")
    repositories_dir.mkdir(exist_ok=True, parents=True)

    repository_dir = repositories_dir.joinpath(repo_name)
    if repository_dir.is_dir():
        return Repository(str(repository_dir))

    return clone_repository(url=target_repo, path=str(repository_dir.resolve()))
