from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from core.models import Film
from core.schemas.film import FilmRead
from core.schemas.pagination import PaginatedResponse
from core.crud.utils.pagination import Paginator

paginator = Paginator(limit=20)


async def get_films(
    session: AsyncSession, request: Request, title: str | None = None, page: int = 1
) -> PaginatedResponse:
    return await paginator.paginate(
        request=request,
        session=session,
        model=Film,
        schema=FilmRead,
        page=page,
        filter=title,
        filter_field=Film.title,
    )
