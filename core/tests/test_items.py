import pytest


@pytest.mark.asyncio
async def test_list_items(client):
    response = await client.get("/api/items/")
    assert response.status_code == 200
