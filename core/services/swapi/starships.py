import logging
from sqlmodel import select
from core.models import Starship
from core.schemas.starship import StarshipCreate
from core.services.swapi.base import SwapiImporterBase

logger = logging.getLogger(__name__)


class StarshipImporter(SwapiImporterBase):
    existing_names: set[str] = set()

    @property
    def resource(self) -> str:
        return "starships"

    async def prefetch_existing(self):
        result = await self.session.execute(select(Starship.name))
        self.existing_names = set(result.scalars().all())

    async def parse(self, raw_data: dict) -> Starship | None:
        name = raw_data.get("name")
        if not name or name in self.existing_names:
            return None

        try:
            valid_data = StarshipCreate(
                name=name,
                model=raw_data.get("model"),
                manufacturer=raw_data.get("manufacturer"),
            )
        except Exception as e:
            logger.warning(f"[starships] Validation failed: {e}")
            return None

        return Starship(**valid_data.model_dump())
