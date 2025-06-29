import logging
from sqlmodel import select
from core.models import Character
from core.models.film import Film
from core.models.starship import Starship
from core.schemas.character import CharacterCreate
from core.services.swapi.base import SwapiImporterBase

logger = logging.getLogger(__name__)


class CharacterImporter(SwapiImporterBase):
    existing_names: set[str] = set()
    film_map: dict[int, Film] = {}
    starship_map: dict[int, Starship] = {}

    @property
    def resource(self) -> str:
        return "people"

    async def prefetch_existing(self):
        # Deduplicate by name
        result = await self.session.execute(select(Character.name))
        self.existing_names = set(result.scalars().all())

        # Prefetch all films
        films_result = await self.session.execute(select(Film))
        self.film_map = {film.id: film for film in films_result.scalars()}

        # Prefetch all starships
        starships_result = await self.session.execute(select(Starship))
        self.starship_map = {
            starship.id: starship for starship in starships_result.scalars()
        }

    def extract_id(self, url: str) -> int:
        return int(url.rstrip("/").split("/")[-1])

    async def parse(self, raw_data: dict) -> Character | None:
        name = raw_data.get("name")
        if not name or name in self.existing_names:
            return None  # skip duplicates

        try:
            valid_data = CharacterCreate(
                name=name,
                gender=raw_data.get("gender"),
                birth_year=raw_data.get("birth_year"),
            )
        except Exception as e:
            logger.warning(f"[characters] Validation failed: {e}")
            return None

        film_ids = [self.extract_id(url) for url in raw_data.get("films", [])]
        starship_ids = [self.extract_id(url) for url in raw_data.get("starships", [])]

        films = [self.film_map[id_] for id_ in film_ids if id_ in self.film_map]
        starships = [
            self.starship_map[id_] for id_ in starship_ids if id_ in self.starship_map
        ]

        return Character(
            name=valid_data.name,
            gender=valid_data.gender,
            birth_year=valid_data.birth_year,
            films=films,
            starships=starships,
        )
