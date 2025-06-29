import pytest
from sqlmodel import select
from core.models import Film, Character, Starship
from sqlalchemy.orm import selectinload


@pytest.mark.asyncio
async def test_film_model_basic_fields(session):
    film = Film(
        title="A New Hope",
        episode_id=4,
        director="George Lucas",
        producer="Gary Kurtz",
        release_date="1977-05-25",
    )

    session.add(film)
    await session.commit()
    await session.refresh(film)

    assert film.id is not None
    assert film.title == "A New Hope"
    assert film.episode_id == 4


@pytest.mark.asyncio
async def test_film_relationships(session):
    film = Film(
        title="The Empire Strikes Back",
        episode_id=5,
        director="Irvin Kershner",
        producer="Gary Kurtz",
        release_date="1980-05-21",
    )

    character = Character(name="Luke Skywalker", gender="male", birth_year="19BBY")
    starship = Starship(name="X-Wing", model="T-65B", manufacturer="Incom Corporation")

    film.characters.append(character)
    film.starships.append(starship)

    session.add(film)
    await session.commit()
    await session.refresh(film)

    # Fetch and assert
    result = await session.execute(
        select(Film)
        .where(Film.id == film.id)
        .options(
            selectinload(Film.characters),
            selectinload(Film.starships),
        )
    )
    fetched = result.scalar_one()

    assert len(fetched.characters) == 1
    assert fetched.characters[0].name == "Luke Skywalker"

    assert len(fetched.starships) == 1
    assert fetched.starships[0].name == "X-Wing"
