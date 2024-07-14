from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from structlog._native import BoundLoggerFilteringAtDebug, BoundLoggerFilteringAtInfo

from gitmind.utils.logger import configured_ref, get_logger


@pytest.fixture()
def reset_configured_ref() -> Generator[None, None, None]:
    configured_ref.value = None
    yield
    configured_ref.value = None


@patch("structlog.configure_once")
@patch("structlog.get_logger")
def test_get_logger_configures_once_if_not_already_configured(
    mock_get_structlog_logger: Mock, mock_configure_once: Mock, reset_configured_ref: None
) -> None:
    get_logger("test_logger")
    mock_configure_once.assert_called_once()
    mock_get_structlog_logger.assert_called_once_with("test_logger")


@patch("structlog.configure_once")
@patch("structlog.get_logger")
def test_get_logger_does_not_reconfigure_if_already_configured(
    mock_get_structlog_logger: Mock, mock_configure_once: Mock, reset_configured_ref: None
) -> None:
    configured_ref.value = True
    get_logger("test_logger")
    mock_configure_once.assert_not_called()
    mock_get_structlog_logger.assert_called_once_with("test_logger")


@patch("structlog.configure_once")
@patch("structlog.get_logger")
def test_get_logger_uses_debug_level_if_debug_env_set(
    mock_get_structlog_logger: Mock, mock_configure_once: Mock, reset_configured_ref: None, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setenv("DEBUG", "1")
    get_logger("debug_logger")
    args, kwargs = mock_configure_once.call_args
    assert kwargs["wrapper_class"] is BoundLoggerFilteringAtDebug


@patch("structlog.configure_once")
@patch("structlog.get_logger")
def test_get_logger_uses_info_level_if_debug_env_not_set(
    mock_get_structlog_logger: Mock, mock_configure_once: Mock, reset_configured_ref: None, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.delenv("DEBUG", raising=False)
    get_logger("info_logger")
    args, kwargs = mock_configure_once.call_args
    assert kwargs["wrapper_class"] is BoundLoggerFilteringAtInfo
