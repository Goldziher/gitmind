import pytest
from _pytest.monkeypatch import MonkeyPatch

from gitmind.utils.env import get_env


def test_get_env_existing_variable(monkeypatch: MonkeyPatch) -> None:
    key = "EXISTING_VAR"
    value = "some_value"

    monkeypatch.setattr("os.environ", {key: value})
    assert get_env(key) == value


def test_get_env_missing_variable_without_raising(monkeypatch: MonkeyPatch) -> None:
    key = "MISSING_VAR"

    result = get_env(key, raise_on_missing=False)
    assert result == ""


def test_get_env_missing_variable_with_raising(monkeypatch: MonkeyPatch) -> None:
    key = "MISSING_VAR"

    with pytest.raises(ValueError):
        get_env(key)
