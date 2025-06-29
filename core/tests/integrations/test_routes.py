from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch
from core.routes.integrations import router

app = FastAPI()
app.include_router(router)


@patch("core.routes.integrations.initialize")
async def test_import_route_starts_background_task(
    mock_initialize, client: AsyncClient
):
    response = await client.post("/api/import/")

    assert response.status_code == 202
    assert response.json() == {"detail": "Import started in the background"}

    mock_initialize.assert_called_once()


@patch("core.routes.integrations.initialize")
async def test_import_route_raises_500_on_exception(
    mock_initialize, client: AsyncClient
):
    mock_initialize.side_effect = RuntimeError("Something went wrong")

    response = await client.post("/api/import/")

    assert response.status_code == 500
    assert response.json() == {"detail": "Something went wrong"}
