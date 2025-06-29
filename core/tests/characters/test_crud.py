import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Character
from core.crud.character import get_characters
from core.schemas.character import CharacterRead
from fastapi import Request


@pytest_asyncio.fixture(scope="function")
async def sample_characters(session: AsyncSession):
    characters = [
        Character(name="Luke Skywalker", gender="male", birth_year="19BBY"),
        Character(name="Leia Organa", gender="female", birth_year="19BBY"),
        Character(name="Han Solo", gender="male", birth_year="29BBY"),
    ]
    session.add_all(characters)
    await session.commit()


async def test_get_characters_returns_paginated_data(
    session: AsyncSession, sample_characters
):
    request = Request({"type": "http", "query_string": b"page=1"})
    paginator = await get_characters(session=session, request=request, page=1)
    assert paginator.count == 3
    assert isinstance(paginator.results[0], CharacterRead)


async def test_search_characters_exact_match(session: AsyncSession, sample_characters):
    request = Request({"type": "http", "query_string": b"page=1"})
    paginator = await get_characters(session, request=request, name="Luke")
    assert len(paginator.results) == 1
    assert paginator.results[0].name == "Luke Skywalker"


async def test_search_characters_partial_match(
    session: AsyncSession, sample_characters
):
    request = Request({"type": "http", "query_string": b"page=1"})
    paginator = await get_characters(session, request=request, name="Sky")
    assert len(paginator.results) == 1
    assert "Skywalker" in paginator.results[0].name


async def test_search_characters_no_match(session: AsyncSession, sample_characters):
    request = Request({"type": "http", "query_string": b"page=1"})
    paginator = await get_characters(session, request=request, name="NotACharacter")
    assert paginator.results == []
