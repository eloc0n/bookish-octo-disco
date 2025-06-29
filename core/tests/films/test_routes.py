import pytest_asyncio
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Film


@pytest_asyncio.fixture
async def films(session: AsyncSession):
    films = [
        Film(
            title="A New Hope",
            episode_id=4,
            director="George Lucas",
            release_date="1977-05-25",
        ),
        Film(
            title="The Empire Strikes Back",
            episode_id=5,
            director="Irvin Kershner",
            release_date="1980-05-21",
        ),
        Film(
            title="Return of the Jedi",
            episode_id=6,
            director="Richard Marquand",
            release_date="1983-05-25",
        ),
    ]
    session.add_all(films)
    await session.commit()


async def test_get_films_basic(client: AsyncClient, films):
    response = await client.get("/api/films/")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 3
    assert len(data["results"]) == 3
    assert any(f["title"] == "A New Hope" for f in data["results"])


async def test_get_films_with_filter(client: AsyncClient, films):
    response = await client.get("/api/films/?title=Empire")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"][0]["title"] == "The Empire Strikes Back"


async def test_get_films_invalid_page(client: AsyncClient):
    response = await client.get("/api/films/?page=0")
    assert response.status_code == 422
