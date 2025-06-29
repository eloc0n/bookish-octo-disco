import pytest

from httpx import Request, Response, HTTPStatusError
from sqlmodel import select
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from sqlalchemy.orm import selectinload
from core.models import Character, Film, Starship
from core.services.swapi.characters import CharacterImporter


@pytest.mark.asyncio
async def test_fetch_page_success(session):
    mock_data = {
        "count": 1,
        "results": [{"name": "Luke", "gender": "male", "birth_year": "19BBY"}],
    }

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock(return_value=None)
    mock_response.json = MagicMock(return_value=mock_data)

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_client
    mock_async_client.__aexit__.return_value = AsyncMock()

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        importer = CharacterImporter(session)
        data = await importer.fetch_page(1)

    assert "results" in data
    assert data["results"][0]["name"] == "Luke"


@pytest.mark.asyncio
async def test_fetch_page_retries_on_500(session):
    request = Request("GET", "https://swapi.dev/api/people/?page=1")
    bad_response = Response(status_code=500, request=request)
    http_error = HTTPStatusError("Mocked 500", request=request, response=bad_response)

    success_data = {
        "count": 1,
        "results": [{"name": "Leia", "gender": "female", "birth_year": "19BBY"}],
    }

    success_response = AsyncMock()
    success_response.status_code = 200
    success_response.raise_for_status = Mock(return_value=None)
    success_response.json = MagicMock(return_value=success_data)

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[http_error, success_response])

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_client
    mock_async_client.__aexit__.return_value = AsyncMock()

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        importer = CharacterImporter(session)
        data = await importer.fetch_page(1)

    assert data["results"][0]["name"] == "Leia"


@pytest.mark.asyncio
async def test_parse_valid_data(session):
    importer = CharacterImporter(session)
    raw = {"name": "Han Solo", "gender": "male", "birth_year": "29BBY"}

    obj = await importer.parse(raw)
    assert obj.name == "Han Solo"
    assert obj.gender == "male"


@pytest.mark.asyncio
async def test_parse_invalid_data(session):
    importer = CharacterImporter(session)
    raw = {"name": None}
    result = await importer.parse(raw)
    assert result is None


@pytest.mark.asyncio
async def test_run_inserts_to_db(session):
    importer = CharacterImporter(session)

    # Patch methods: fetch_all and parse
    importer.fetch_all = AsyncMock(
        return_value=[
            {"name": "Luke Skywalker", "gender": "male", "birth_year": "19BBY"},
            {"name": "Leia Organa", "gender": "female", "birth_year": "19BBY"},
        ]
    )

    # run() uses parse(), which is already implemented
    await importer.run()

    result = await session.execute(select(Character))
    characters = result.scalars().all()

    assert len(characters) == 2
    assert characters[0].name == "Luke Skywalker"


@pytest.mark.asyncio
async def test_run_skips_invalid_records(session):
    importer = CharacterImporter(session)

    importer.fetch_all = AsyncMock(
        return_value=[
            {"name": "Valid One", "gender": "n/a", "birth_year": "0BBY"},
            {"bad_field": True},  # Will fail parse()
        ]
    )

    await importer.run()

    result = await session.execute(select(Character))
    characters = result.scalars().all()

    assert len(characters) == 1
    assert characters[0].name == "Valid One"


@pytest.mark.asyncio
async def test_parse_valid_data_with_relations(session):
    importer = CharacterImporter(session)

    # Simulate preloaded film and starship maps
    importer.film_map = {1: Film(id=1, title="A New Hope")}
    importer.starship_map = {5: Starship(id=5, name="X-Wing", model="T-65B")}

    raw = {
        "name": "Luke Skywalker",
        "gender": "male",
        "birth_year": "19BBY",
        "films": ["https://swapi.dev/api/films/1/"],
        "starships": ["https://swapi.dev/api/starships/5/"],
    }

    character = await importer.parse(raw)

    assert character.name == "Luke Skywalker"
    assert character.films[0].title == "A New Hope"
    assert character.starships[0].name == "X-Wing"


@pytest.mark.asyncio
async def test_run_inserts_with_relations(session):
    film = Film(id=1, title="A New Hope", release_date="1977-05-25")
    starship = Starship(id=5, name="X-Wing", model="T-65B")

    session.add_all([film, starship])
    await session.commit()

    importer = CharacterImporter(session)
    await importer.prefetch_existing()

    importer.fetch_all = AsyncMock(
        return_value=[
            {
                "name": "Luke Skywalker",
                "gender": "male",
                "birth_year": "19BBY",
                "films": ["https://swapi.dev/api/films/1/"],
                "starships": ["https://swapi.dev/api/starships/5/"],
            }
        ]
    )

    await importer.run()

    result = await session.execute(
        select(Character).options(
            selectinload(Character.films), selectinload(Character.starships)
        )
    )
    characters = result.scalars().all()

    assert len(characters) == 1
    luke = characters[0]
    assert luke.name == "Luke Skywalker"
    assert len(luke.films) == 1
    assert luke.films[0].title == "A New Hope"
    assert len(luke.starships) == 1
    assert luke.starships[0].name == "X-Wing"
