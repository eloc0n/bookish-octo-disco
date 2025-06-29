import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import HTTPStatusError, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from core.services.swapi.base import SwapiImporterBase


class DummyImporter(SwapiImporterBase):
    @property
    def resource(self):
        return "dummy"

    async def parse(self, raw_data: dict):
        return {"parsed": raw_data}


@pytest.mark.asyncio
async def test_fetch_page_success(monkeypatch):
    importer = DummyImporter(session=MagicMock(spec=AsyncSession))

    mock_data = {"results": [{"name": "Test"}]}
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value=mock_data)

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get.return_value = mock_response

    monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: client_mock)

    result = await importer.fetch_page(1)
    assert result == mock_data


@pytest.mark.asyncio
async def test_fetch_page_malformed_response(monkeypatch):
    importer = DummyImporter(session=MagicMock(spec=AsyncSession))

    mock_data = {"not_results": True}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json = MagicMock(return_value=mock_data)

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get.return_value = mock_response

    monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: client_mock)

    with pytest.raises(ValueError, match="Malformed response"):
        await importer.fetch_page(1)


@pytest.mark.asyncio
async def test_fetch_page_non_retryable_http_error(monkeypatch):
    importer = DummyImporter(session=MagicMock(spec=AsyncSession))

    response_mock = MagicMock(spec=Response)
    response_mock.status_code = 404
    error = HTTPStatusError(
        "Error", request=MagicMock(spec=Request), response=response_mock
    )

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get.side_effect = error

    monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: client_mock)

    with pytest.raises(HTTPStatusError):
        await importer.fetch_page(1)
