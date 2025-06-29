import pytest
from unittest.mock import AsyncMock, patch

from core.crud.integrations import run_all_importers


@pytest.mark.asyncio
@patch("core.crud.integrations.FilmImporter")
@patch("core.crud.integrations.StarshipImporter")
@patch("core.crud.integrations.CharacterImporter")
@patch("core.crud.integrations.async_session")
@patch("core.crud.integrations.logger")
async def test_run_all_importers_failure(
    logger_mock, async_session_mock, char_imp_mock, ship_imp_mock, film_imp_mock
):
    """
    If one importer fails, logs the error but doesn't crash the test
    """
    mock_session = AsyncMock()
    async_session_mock.return_value.__aenter__.return_value = mock_session

    film_imp_mock.return_value.run = AsyncMock()
    ship_imp_mock.return_value.run = AsyncMock(side_effect=RuntimeError("Boom"))
    char_imp_mock.return_value.run = AsyncMock()

    await run_all_importers()

    film_imp_mock.return_value.run.assert_awaited_once()
    ship_imp_mock.return_value.run.assert_awaited_once()
    char_imp_mock.return_value.run.assert_not_called()

    logger_mock.exception.assert_called_once()


@pytest.mark.asyncio
@patch("core.crud.integrations.FilmImporter")
@patch("core.crud.integrations.StarshipImporter")
@patch("core.crud.integrations.CharacterImporter")
@patch("core.crud.integrations.async_session")
async def test_run_all_importers_success(
    async_session_mock, char_imp_mock, ship_imp_mock, film_imp_mock
):
    """
    All importers run successfully
    """
    mock_session = AsyncMock()
    async_session_mock.return_value.__aenter__.return_value = mock_session

    film_imp_mock.return_value.run = AsyncMock()
    ship_imp_mock.return_value.run = AsyncMock()
    char_imp_mock.return_value.run = AsyncMock()

    await run_all_importers()

    film_imp_mock.assert_called_once_with(mock_session)
    ship_imp_mock.assert_called_once_with(mock_session)
    char_imp_mock.assert_called_once_with(mock_session)

    film_imp_mock.return_value.run.assert_awaited_once()
    ship_imp_mock.return_value.run.assert_awaited_once()
    char_imp_mock.return_value.run.assert_awaited_once()
