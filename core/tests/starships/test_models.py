import pytest
from sqlmodel import select
from core.models import Starship, Character, Film
from core.models.links import CharacterStarshipLink, StarshipFilmLink
from sqlalchemy.orm import selectinload


@pytest.mark.asyncio
async def test_create_starship(session):
    starship = Starship(
        name="Millennium Falcon",
        model="YT-1300",
        manufacturer="Corellian Engineering Corporation",
    )
    session.add(starship)
    await session.commit()
    await session.refresh(starship)

    assert starship.id is not None
    assert starship.name == "Millennium Falcon"
    assert starship.model == "YT-1300"
    assert starship.manufacturer == "Corellian Engineering Corporation"


@pytest.mark.asyncio
async def test_starship_relationships(session):
    # Create related Film and Character
    film = Film(title="A New Hope", release_date="1977-05-25", episode_id=4)
    pilot = Character(name="Han Solo", gender="male", birth_year="29BBY")

    # Create starship and link relationships
    starship = Starship(
        name="Millennium Falcon",
        model="YT-1300",
        manufacturer="Corellian Engineering Corporation",
        films=[film],
        pilots=[pilot],
    )

    session.add(starship)
    await session.commit()
    await session.refresh(starship)

    # Reload to assert links
    result = await session.execute(
        select(Starship)
        .where(Starship.id == starship.id)
        .options(
            selectinload(Starship.films),
            selectinload(Starship.pilots),
        )
    )
    fetched = result.scalar_one()

    assert len(fetched.films) == 1
    assert fetched.films[0].title == "A New Hope"

    assert len(fetched.pilots) == 1
    assert fetched.pilots[0].name == "Han Solo"

    # Check link tables manually
    result = await session.execute(select(StarshipFilmLink))
    film_links = result.scalars().all()
    assert len(film_links) == 1

    result = await session.execute(select(CharacterStarshipLink))
    pilot_links = result.scalars().all()
    assert len(pilot_links) == 1
