from git import Commit, PathLike, Repo


def clone_repository(repo_path: PathLike, branch_name: str, target_path: PathLike) -> Repo:
    """Clone a Git repository.

    Args:
        repo_path: The URL or path of the Git repository.
        branch_name: The name of the branch to clone.
        target_path: The path to clone the repository to.

    Returns:
        The cloned Git repository.
    """
    return Repo.clone_from(url=repo_path, to_path=target_path, branch=branch_name)


def get_commits(repo_path: PathLike) -> list[Commit]:
    """Get the commits of a Git repository.

    Args:
        repo_path: The path to the Git repository.

    Returns:
        The list of commits in the repository.
    """
    repo = Repo(repo_path)
    return list(repo.iter_commits())
