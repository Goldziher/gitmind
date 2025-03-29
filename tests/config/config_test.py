from pathlib import Path

import pytest
from tomllib import loads  # type: ignore[import-not-found]

from gitmind.config import GitMindSettings


@pytest.fixture
def pyproject_file(test_settings: GitMindSettings) -> str:  # type: ignore[misc]
    filtered_items = [(k, v) for k, v in test_settings.model_dump().items() if v is not None]

    settings = "\n".join(
        [f"{k}={'"' + str(v) + '"' if k != 'provider_api_key' else '"' + 'abc' + '"'}" for k, v in filtered_items]
    )

    values = f"""
[project]
name = "test"
requires-python = ">=3.9"

[tool.gitmind]
{settings}
""".strip()

    assert loads(values)

    file = Path("pyproject.toml")
    file.write_text(values)
    yield file
    file.unlink()


def test_reading_pyproject_correctly(pyproject_file: Path, test_settings: GitMindSettings) -> None:
    settings = GitMindSettings()  # type: ignore[call-arg]

    for k in settings.model_dump():
        if k == "provider_api_key":
            continue

        assert getattr(settings, k) == getattr(test_settings, k)
