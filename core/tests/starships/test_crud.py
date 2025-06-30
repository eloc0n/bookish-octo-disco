import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Starship
from core.crud.starship import get_starships, get_starship
from core.crud.starship import paginator
from fastapi import HTTPException


class MockRequest:
    def __init__(self, url: str):
        self.url = url


@pytest_asyncio.fixture
async def sample_starships(session: AsyncSession):
    starships = [
        Starship(name="X-Wing", model="T-65B", manufacturer="Incom Corporation"),
        Starship(
            name="TIE Fighter",
            model="Twin Ion Engine",
            manufacturer="Sienar Fleet Systems",
        ),
        Starship(
            name="Millennium Falcon",
            model="YT-1300",
            manufacturer="Corellian Engineering Corporation",
        ),
    ]
    session.add_all(starships)
    await session.commit()


async def test_get_starships_without_filter(session: AsyncSession, sample_starships):
    request = MockRequest("http://test/api/starships/")
    response = await get_starships(session=session, request=request)

    assert response.count == 3
    assert len(response.results) == 3
    names = [s["name"] for s in response.model_dump()["results"]]
    assert "X-Wing" in names
    assert "Millennium Falcon" in names


async def test_get_starships_with_filter(session: AsyncSession, sample_starships):
    request = MockRequest("http://test/api/starships/")
    response = await get_starships(session=session, request=request, name="X-Wing")

    assert response.count == 1
    assert response.results[0].name == "X-Wing"


async def test_get_starships_pagination(session: AsyncSession, sample_starships):
    request = MockRequest("http://test/api/starships/")
    # Small page size to simulate pagination
    paginator.limit = 2

    page_1 = await get_starships(session=session, request=request, page=1)
    page_2 = await get_starships(session=session, request=request, page=2)

    assert page_1.count == 3
    assert len(page_1.results) == 2
    assert page_1.next is not None
    assert page_1.previous is None

    assert len(page_2.results) == 1
    assert page_2.next is None
    assert page_2.previous is not None


async def test_get_starship_by_id(session, sample_starships):
    result = await get_starship(2, session)
    assert result.name == "TIE Fighter"


async def test_get_starship_by_id_not_found(session, sample_starships):
    with pytest.raises(HTTPException):
        await get_starship(999, session)
