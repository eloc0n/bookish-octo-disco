import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from core.models import Film
from core.crud.film import get_film, get_films


class MockRequest:
    def __init__(self, url: str):
        self.url = url


@pytest_asyncio.fixture
async def sample_films(session: AsyncSession):
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


async def test_get_films_basic(session: AsyncSession, sample_films):
    request = MockRequest("http://test/api/films/")
    response = await get_films(session, request)

    assert response.count == 3
    assert len(response.results) == 3
    assert any(f.title == "A New Hope" for f in response.results)


async def test_get_films_with_filter(session: AsyncSession, sample_films):
    request = MockRequest("http://test/api/films/?title=Empire")
    response = await get_films(session, request, title="Empire")

    assert response.count == 1
    assert response.results[0].title == "The Empire Strikes Back"


async def test_get_films_out_of_bounds(session: AsyncSession, sample_films):
    request = MockRequest("http://test/api/films/?page=999")
    response = await get_films(session, request, page=999)

    assert response.results == []
    assert response.next is None
    assert response.previous is not None


async def test_get_film_by_id(session, sample_films):
    result = await get_film(1, session)
    assert result.title == "A New Hope"


async def test_get_film_by_id_not_found(session, sample_films):
    with pytest.raises(HTTPException):
        await get_film(999, session)
