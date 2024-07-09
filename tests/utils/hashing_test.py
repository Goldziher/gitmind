from git_critic.utils.hashing import get_sha_hash


def test_get_sha_hash() -> None:
    assert get_sha_hash("content") == "ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73"
