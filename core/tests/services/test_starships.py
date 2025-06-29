import pytest
from unittest.mock import AsyncMock
from sqlmodel import select

from core.models import Starship
from core.services.swapi.starships import StarshipImporter


@pytest.mark.asyncio
async def test_parse_valid_starship(session):
    importer = StarshipImporter(session)
    raw = {
        "name": "X-Wing",
        "model": "T-65 X-wing",
        "manufacturer": "Incom Corporation",
    }

    obj = await importer.parse(raw)
    assert obj.name == "X-Wing"
    assert obj.model == "T-65 X-wing"
    assert obj.manufacturer == "Incom Corporation"


@pytest.mark.asyncio
async def test_parse_invalid_starship(session):
    importer = StarshipImporter(session)
    raw = {
        "name": None,
        "model": "Broken",
    }
    result = await importer.parse(raw)
    assert result is None


@pytest.mark.asyncio
async def test_run_inserts_starships(session):
    importer = StarshipImporter(session)

    importer.fetch_all = AsyncMock(
        return_value=[
            {
                "name": "Millennium Falcon",
                "model": "YT-1300 light freighter",
                "manufacturer": "Corellian Engineering Corporation",
            },
            {
                "name": "TIE Fighter",
                "model": "Twin Ion Engine Fighter",
                "manufacturer": "Sienar Fleet Systems",
            },
        ]
    )

    await importer.run()

    result = await session.execute(select(Starship))
    starships = result.scalars().all()

    assert len(starships) == 2
    assert starships[0].name == "Millennium Falcon"
