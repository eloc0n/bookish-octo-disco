import pytest_asyncio
from core.models.character import Character
from core.models.film import Film
from core.models.starship import Starship
from core.schemas.character import CharacterRead
from core.schemas.pagination import PaginatedResponse
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest_asyncio.fixture
async def characters_with_links(session: AsyncSession):
    film = Film(title="A New Hope", release_date="1977-05-25")
    starship = Starship(name="X-Wing", model="T-65B")

    characters = [
        Character(
            name="Luke Skywalker",
            gender="male",
            birth_year="19BBY",
            films=[film],
            starships=[starship],
        ),
        Character(name="Leia Organa", gender="female", birth_year="19BBY"),
        Character(name="Han Solo", gender="male", birth_year="29BBY"),
    ]

    session.add_all(characters)
    await session.commit()


async def test_list_characters(client, characters_with_links):
    response = await client.get("/api/characters/")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3
    assert len(data["results"]) == 3

    names = [c["name"] for c in data["results"]]
    assert "Luke Skywalker" in names


async def test_search_characters_found(client, characters_with_links):
    response = await client.get("/api/characters/?name=Luke")
    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Luke Skywalker"


async def test_search_characters_partial_match(client, characters_with_links):
    response = await client.get("/api/characters/?name=Sky")
    assert response.status_code == 200

    data = response.json()
    names = [r["name"] for r in data["results"]]
    assert any("Skywalker" in name for name in names)


async def test_search_characters_not_found(client, characters_with_links):
    response = await client.get("/api/characters/?name=NotACharacter")
    assert response.status_code == 200
    assert response.json()["results"] == []


async def test_list_characters_invalid_page(client, characters_with_links):
    response = await client.get("/api/characters/?page=999")
    assert response.status_code == 200
    assert response.json()["results"] == []


async def test_search_response_schema(client, characters_with_links):
    response = await client.get("/api/characters/?name=Han")
    assert response.status_code == 200

    data = response.json()
    parsed = [CharacterRead(**item) for item in data["results"]]
    assert parsed[0].name == "Han Solo"


async def test_response_schema_matches(client, characters_with_links):
    response = await client.get("/api/characters/")
    assert response.status_code == 200

    parsed = PaginatedResponse[CharacterRead].model_validate(response.json())
    assert parsed.count == 3
    assert isinstance(parsed.results[0], CharacterRead)
