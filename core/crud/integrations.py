import asyncio
from core.database.session import async_session
from core.services.swapi import CharacterImporter, FilmImporter, StarshipImporter
import logging

logger = logging.getLogger(__name__)


async def run_all_importers():
    """
    Run all SWAPI importers in order.

    This function sequentially imports films, then starships, and finally characters,
    ensuring that all many-to-many dependencies are satisfied.
    Logs progress and handles any exceptions during the import process.
    """
    async with async_session() as session:
        try:
            await FilmImporter(session).run()
            await StarshipImporter(session).run()
            await CharacterImporter(session).run()
            logger.info("All importers finished successfully.")
        except Exception:
            logger.exception("Importing failed")


def initialize():
    asyncio.create_task(run_all_importers())
