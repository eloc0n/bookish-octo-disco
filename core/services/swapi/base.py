import abc
import asyncio
import math
import logging
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession
from core.config import CHUNK_SIZE, MAX_RETRIES, RETRYABLE_CODES, SWAPI_BASE_URL

logger = logging.getLogger(__name__)


class SwapiImporterBase(abc.ABC):
    """
    Abstract base class for importing paginated resources from the Star Wars API (SWAPI).

    Responsibilities:
    - Fetch paginated data from a SWAPI resource endpoint.
    - Parse each item into a database model instance.
    - Deduplicate data using a `prefetch_existing()` hook.
    - Insert parsed objects into the database in batches.
    - Handle network errors, retries, and malformed responses gracefully.

    Subclasses must implement:
        - `resource`: the SWAPI resource name (e.g. 'people', 'films', 'starships')
        - `parse()`: logic to convert a raw SWAPI dict into a database model

    Optional override:
        - `prefetch_existing()`: preload existing DB entries to support deduplication

    Notes:
    - Uses `httpx.AsyncClient` with retry logic for robustness.
    - Designed to be subclassed by specific importers for each resource type.
    - Ensures clean logging for monitoring import progress and errors.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    @abc.abstractmethod
    def resource(self) -> str:
        """SWAPI resource name (e.g., 'people', 'films')."""
        raise NotImplementedError

    async def prefetch_existing(self) -> None:
        """
        Optional hook to prefetch existing data for deduplication.
        Override to populate self.existing_names, self.existing_titles, etc.
        """
        pass

    @abc.abstractmethod
    async def parse(self, raw_data: dict):
        """Parse SWAPI object into a model and add to session."""
        raise NotImplementedError

    async def fetch_page(self, page: int) -> dict:
        """Perform api call per page"""
        url = f"{SWAPI_BASE_URL}/{self.resource}/?page={page}"

        for attempt in range(MAX_RETRIES):
            try:
                # Disabling SSL verification with 'verify=false'
                async with httpx.AsyncClient(verify=False, timeout=10) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if not isinstance(data, dict) or "results" not in data:
                        raise ValueError(f"Malformed response: {data}")

                    return data

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status in RETRYABLE_CODES:
                    logger.warning(
                        f"[{self.resource}] HTTP {status} on {url}, retrying ({attempt + 1}/{MAX_RETRIES})"
                    )
                    await asyncio.sleep(2**attempt)
                else:
                    logger.error(f"[{self.resource}] Non-retryable HTTP error: {e}")
                    raise

            except httpx.RequestError as e:
                logger.warning(
                    f"[{self.resource}] Network error on {url}: {e}, retrying ({attempt + 1}/{MAX_RETRIES})"
                )
                await asyncio.sleep(2**attempt)

            except Exception as e:
                logger.error(f"[{self.resource}] Unexpected error: {e}")
                raise

        raise RuntimeError(
            f"[{self.resource}] Failed to fetch page {page} after {MAX_RETRIES} attempts."
        )

    async def fetch_all(self) -> list[dict]:
        """Collect all results from paginated endpoints"""
        logger.info(f"[{self.resource}] Fetching all data...")
        all_results = []

        first_page = await self.fetch_page(1)
        all_results.extend(first_page["results"])

        total_count = first_page.get("count", 0)
        page_size = len(first_page["results"]) or 1
        total_pages = math.ceil(total_count / page_size)

        for page in range(2, total_pages + 1):
            logger.info(f"[{self.resource}] Fetching page {page}/{total_pages}")
            page_data = await self.fetch_page(page)
            all_results.extend(page_data.get("results", []))

        return all_results

    async def run(self):
        """Main drive of the importer"""
        logger.info(f"[{self.resource}] Starting import process...")

        await self.prefetch_existing()

        raw_data_list = await self.fetch_all()
        objects = []

        for raw in raw_data_list:
            try:
                if obj := await self.parse(raw):
                    objects.append(obj)
            except Exception as e:
                logger.error(f"[{self.resource}] Skipping invalid record: {e}")

        if not objects:
            logger.warning(f"[{self.resource}] No valid records to insert.")
            return

        logger.info(f"[{self.resource}] Inserting {len(objects)} records in batches...")

        for i in range(0, len(objects), CHUNK_SIZE):
            self.session.add_all(objects[i : i + CHUNK_SIZE])
            await self.session.commit()

        logger.info(f"[{self.resource}] Import completed successfully.")
