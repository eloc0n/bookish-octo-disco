import pytest
import pytest_asyncio

from sqlmodel.ext.asyncio.session import AsyncSession
from core.crud.utils.pagination import Paginator
from core.schemas.character import CharacterRead
from core.models import Character


@pytest_asyncio.fixture
async def many_characters(session: AsyncSession):
    session.add_all(
        [
            Character(name=f"Test Character {i}", gender="n/a", birth_year="0BBY")
            for i in range(50)
        ]
    )
    await session.commit()


class MockRequest:
    def __init__(self, url: str):
        self.url = url


async def test_paginator_returns_correct_page(session: AsyncSession, many_characters):
    paginator = Paginator(limit=10)
    request = MockRequest("http://test/api/characters/")

    page_2 = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=2,
    )

    assert page_2.count == 50
    assert len(page_2.results) == 10
    assert page_2.previous is not None
    assert page_2.next is not None
    assert "page=1" in page_2.previous
    assert "page=3" in page_2.next


async def test_paginator_first_and_last_page(session: AsyncSession, many_characters):
    paginator = Paginator(limit=25)
    request = MockRequest("http://test/api/characters/")

    first_page = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=1,
    )
    assert first_page.previous is None
    assert "page=2" in first_page.next

    last_page = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=2,
    )
    assert "page=1" in last_page.previous
    assert last_page.next is None


async def test_paginator_out_of_bounds_page(session: AsyncSession, many_characters):
    paginator = Paginator(limit=20)
    request = MockRequest("http://test/api/characters/")
    response = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=999,
    )

    assert response.results == []
    assert response.previous is not None
    assert response.next is None


async def test_paginator_invalid_page_raises(session: AsyncSession):
    paginator = Paginator()
    request = MockRequest("http://test/api/characters/")

    with pytest.raises(ValueError, match="Page number must be >= 1"):
        await paginator.paginate(
            request=request,
            session=session,
            model=Character,
            schema=CharacterRead,
            page=0,
        )


async def test_paginator_filtering(session: AsyncSession):
    # Add characters with varying names
    session.add_all(
        [
            Character(name="Luke Skywalker", gender="male", birth_year="19BBY"),
            Character(name="Leia Organa", gender="female", birth_year="19BBY"),
            Character(name="Han Solo", gender="male", birth_year="29BBY"),
        ]
    )
    await session.commit()

    paginator = Paginator(limit=10)
    request = MockRequest("http://test/api/characters/")

    # Search for characters with 'luke' in the name (case-insensitive)
    page = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=1,
        filter="luke",
        filter_field=Character.name,
    )

    assert page.count == 1
    assert len(page.results) == 1
    assert page.results[0].name == "Luke Skywalker"


async def test_paginator_filtering_no_results(session: AsyncSession):
    paginator = Paginator(limit=10)
    request = MockRequest("http://test/api/characters/")

    page = await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=1,
        filter="vader",  # No match
        filter_field=Character.name,
    )

    assert page.count == 0
    assert page.results == []
    assert page.previous is None
    assert page.next is None
