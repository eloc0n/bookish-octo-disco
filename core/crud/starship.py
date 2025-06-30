from fastapi import Request, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Starship
from core.schemas.starship import StarshipRead
from core.schemas.pagination import PaginatedResponse
from core.crud.utils.pagination import Paginator

paginator = Paginator(limit=20)


async def get_starships(
    session: AsyncSession,
    request: Request,
    name: str | None = None,
    page: int = 1,
) -> PaginatedResponse:
    return await paginator.paginate(
        request=request,
        session=session,
        model=Starship,
        schema=StarshipRead,
        page=page,
        filter=name,
        filter_field=Starship.name,
    )


async def get_starship(starship_id: int, session: AsyncSession) -> StarshipRead:
    starship = await session.get(Starship, starship_id)
    if not starship:
        raise HTTPException(status_code=404, detail="Starship not found")
    return starship
