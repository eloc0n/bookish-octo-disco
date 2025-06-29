import pytest
from unittest.mock import AsyncMock
from sqlmodel import select

from core.models import Film
from core.services.swapi.films import FilmImporter


@pytest.mark.asyncio
async def test_parse_valid_film(session):
    importer = FilmImporter(session)
    raw = {
        "title": "A New Hope",
        "episode_id": 1,
        "release_date": "1977-05-25",
        "director": "George Lucas",
        "producer": "Gary Kurtz, Rick McCallum",
    }

    film = await importer.parse(raw)
    assert film.title == "A New Hope"
    assert film.release_date == "1977-05-25"
    assert film.director == "George Lucas"
    assert film.producer == "Gary Kurtz, Rick McCallum"


@pytest.mark.asyncio
async def test_parse_invalid_film(session):
    importer = FilmImporter(session)
    raw = {"title": None}  # Missing required fields
    result = await importer.parse(raw)
    assert result is None


@pytest.mark.asyncio
async def test_run_inserts_films(session):
    importer = FilmImporter(session)

    importer.fetch_all = AsyncMock(
        return_value=[
            {
                "title": "A New Hope",
                "episode_id": 1,
                "release_date": "1977-05-25",
                "director": "George Lucas",
                "producer": "Gary Kurtz, Rick McCallum",
            },
            {
                "title": "The Empire Strikes Back",
                "episode_id": 2,
                "release_date": "1980-05-17",
                "director": "Irvin Kershner",
                "producer": "Gary Kurtz",
            },
        ]
    )

    await importer.run()

    result = await session.execute(select(Film))
    films = result.scalars().all()

    assert len(films) == 2
    titles = [f.title for f in films]
    assert "A New Hope" in titles
    assert "The Empire Strikes Back" in titles


@pytest.mark.asyncio
async def test_run_skips_duplicates(session):
    # Pre-insert a film
    session.add(
        Film(
            title="A New Hope",
            episode_id=1,
            release_date="1977-05-25",
            director="George Lucas",
            producer="Gary Kurtz, Rick McCallum",
        )
    )
    await session.commit()

    importer = FilmImporter(session)
    importer.fetch_all = AsyncMock(
        return_value=[
            {
                "title": "A New Hope",
                "episode_id": 1,
                "release_date": "1977-05-25",
                "director": "George Lucas",
                "producer": "Gary Kurtz, Rick McCallum",
            }
        ]
    )

    await importer.run()
    result = await session.execute(select(Film))
    films = result.scalars().all()

    # Still 1 film in DB
    assert len(films) == 1
