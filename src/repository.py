from git import Commit, Repo


def clone_repository(repo_url: str, branch_name: str, repo_path: str) -> Repo:
    """Clone a Git repository.

    Args:
        repo_url: The URL of the Git repository.
        branch_name: The name of the branch to clone.
        repo_path: The path to clone the repository to.

    Returns:
        The cloned Git repository.
    """
    return Repo.clone_from(repo_url, repo_path, branch=branch_name)


def get_commits(repo_path: str) -> list[Commit]:
    """Get the commits of a Git repository.

    Args:
        repo_path: The path to the Git repository.

    Returns:
        The list of commits in the repository.
    """
    repo = Repo(repo_path)
    return list(repo.iter_commits())
