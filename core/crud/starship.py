from fastapi import Request
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
