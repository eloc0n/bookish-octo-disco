import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Character, Film, Starship


@pytest_asyncio.fixture
async def character_with_relations(session: AsyncSession):
    film = Film(title="A New Hope", release_date="1977-05-25")
    starship = Starship(name="X-Wing", model="T-65B")

    character = Character(
        name="Luke Skywalker",
        gender="male",
        birth_year="19BBY",
        films=[film],
        starships=[starship],
    )

    session.add(character)
    await session.commit()
    await session.refresh(character)
    return character


async def test_character_relationships(
    session: AsyncSession, character_with_relations: Character
):
    char = await session.get(Character, character_with_relations.id)
    await session.refresh(char, attribute_names=["films", "starships"])

    assert char.name == "Luke Skywalker"
    assert len(char.films) == 1
    assert char.films[0].title == "A New Hope"

    assert len(char.starships) == 1
    assert char.starships[0].name == "X-Wing"


async def test_create_character_with_relations(session: AsyncSession):
    film = Film(title="Empire Strikes Back", release_date="1980-05-21")
    starship = Starship(name="Millennium Falcon", model="YT-1300")

    character = Character(
        name="Han Solo",
        gender="male",
        birth_year="29BBY",
        films=[film],
        starships=[starship],
    )

    session.add(character)
    await session.commit()
    await session.refresh(character, attribute_names=["films", "starships"])

    assert character.id is not None
    assert len(character.films) == 1
    assert character.films[0].title == "Empire Strikes Back"
    assert len(character.starships) == 1
    assert character.starships[0].name == "Millennium Falcon"
