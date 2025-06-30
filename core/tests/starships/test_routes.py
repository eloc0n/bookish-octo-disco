import pytest_asyncio
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Starship


@pytest_asyncio.fixture
async def sample_starships(session: AsyncSession):
    starships = [
        Starship(name="X-Wing", model="T-65B", manufacturer="Incom Corporation"),
        Starship(
            name="TIE Fighter",
            model="Twin Ion Engine",
            manufacturer="Sienar Fleet Systems",
        ),
    ]
    session.add_all(starships)
    await session.commit()


async def test_get_starships_basic(client: AsyncClient, sample_starships):
    response = await client.get("/api/starships/")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert any(s["name"] == "X-Wing" for s in data["results"])


async def test_get_starships_with_filter(client: AsyncClient, sample_starships):
    response = await client.get("/api/starships/?name=wing")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"][0]["name"] == "X-Wing"


async def test_get_starships_invalid_page(client: AsyncClient):
    response = await client.get("/api/starships/?page=0")
    assert response.status_code == 422


async def test_get_starship_by_id(client, sample_starships):
    # assuming starship with id=1 exists
    response = await client.get("/api/starships/1/")
    assert response.status_code == 200
    assert response.json()["id"] == 1
