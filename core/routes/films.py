from fastapi import APIRouter, Depends, Query, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database.session import get_session
from core.schemas import FilmRead
from core.crud.film import get_films, get_film
from core.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/films", tags=["Films"])


@router.get("/", response_model=PaginatedResponse[FilmRead])
async def films(
    request: Request,
    page: int = Query(1, ge=1),
    title: str | None = Query(None, min_length=1),
    session: AsyncSession = Depends(get_session),
):
    return await get_films(session, request, title, page)


@router.get("/{film_id}/", response_model=FilmRead)
async def film(film_id: int, session: AsyncSession = Depends(get_session)):
    return await get_film(film_id, session)
