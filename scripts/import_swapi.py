import asyncio
from core.database.session import async_session
from core.services.swapi.characters import CharacterImporter
from core.services.swapi.films import FilmImporter
from core.services.swapi.starships import StarshipImporter


async def main():
    async with async_session() as session:
        await FilmImporter(session).run()
        await StarshipImporter(session).run()
        await CharacterImporter(session).run()


if __name__ == "__main__":
    asyncio.run(main())
