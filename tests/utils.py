from unittest.mock import AsyncMock, Mock


def create_mock_client(return_value: str = "", exc: Exception | None = None) -> AsyncMock:
    mock_create_completions = AsyncMock()
    if exc:
        mock_create_completions.side_effect = exc
    else:
        mock_create_completions.return_value = return_value

    return Mock(
        get_or_create_instance=Mock(
            create_completions=mock_create_completions,
        ),
        return_value=Mock(
            create_completions=mock_create_completions,
        ),
        create_completions=mock_create_completions,
    )
