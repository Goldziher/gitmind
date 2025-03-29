from pathlib import Path

import pytest
from click import Choice
from click.testing import CliRunner

from gitmind.cli import cli
from gitmind.cli._utils import get_global_option_fields


def test_cli_entry_point_help(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["--help"])
    global_option_fields = get_global_option_fields()
    assert result.exit_code == 0

    for param_name, _, option_type in global_option_fields:
        assert param_name in result.output
        if isinstance(option_type, Choice):
            assert option_type.choices[0] in result.output


@pytest.mark.parametrize(
    "opts",
    (
        (
            f"--target-repo={Path(__file__).parent.parent.parent.resolve()}",
            "--provider-name=openai",
            "--provider-api-key=abc-jeronimo",
            "--provider-model=gpt-3.5-turbo",
        ),
        (
            f"--target-repo={Path(__file__).parent.parent.parent.resolve()}",
            "--provider-name=groq",
            "--provider-api-key=abc-jeronimo",
            "--provider-model=llama3-70b-8192",
        ),
        (
            f"--target-repo={Path(__file__).parent.parent.parent.resolve()}",
            "--provider-name=azure-openai",
            "--provider-api-key=abc-jeronimo",
            "--provider-endpoint-url=https://api.openai.com",
            "--provider-deployment-id=v1",
            "--provider-model=gpt-3.5-turbo",
        ),
    ),
)
def test_cli_settings_init(cli_runner: CliRunner, opts: tuple[str, ...]) -> None:
    result = cli_runner.invoke(cli, [*opts, "commit", "--help"])
    assert result.exit_code == 0


def test_cli_settings_init_err_when_missing_required_opts(cli_runner: CliRunner) -> None:
    opts = [
        f"--target-repo={Path(__file__).parent.parent.parent.resolve()}",
        "--provider-name=openai",
        "--provider-api-key=abc-jeronimo",
        "--provider-model=gpt-3.5-turbo",
    ]

    for i in range(len(opts)):
        result = cli_runner.invoke(cli, opts[:i] + opts[i + 1 :] + ["commit", "--help"])
        assert result.exit_code != 0
