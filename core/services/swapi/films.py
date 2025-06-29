import logging
from sqlmodel import select
from core.models import Film
from core.schemas.film import FilmCreate
from core.services.swapi.base import SwapiImporterBase

logger = logging.getLogger(__name__)


class FilmImporter(SwapiImporterBase):
    existing_titles: set[str] = set()

    @property
    def resource(self) -> str:
        return "films"

    async def prefetch_existing(self):
        result = await self.session.execute(select(Film.title))
        self.existing_titles = set(result.scalars().all())

    async def parse(self, raw_data: dict) -> Film | None:
        title = raw_data.get("title")
        if not title or title in self.existing_titles:
            return None

        try:
            valid_data = FilmCreate(
                title=title,
                release_date=raw_data.get("release_date"),
                episode_id=raw_data.get("episode_id"),
                director=raw_data.get("director"),
                producer=raw_data.get("producer"),
            )
        except Exception as e:
            logger.warning(f"[films] Validation failed: {e}")
            return None

        return Film(**valid_data.model_dump())
