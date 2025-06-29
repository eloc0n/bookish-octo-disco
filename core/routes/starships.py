from fastapi import APIRouter, Depends, Query, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database.session import get_session
from core.schemas import StarshipRead
from core.crud.starship import get_starships
from core.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/starships", tags=["Starships"])


@router.get("/", response_model=PaginatedResponse[StarshipRead])
async def starships(
    request: Request,
    page: int = Query(1, ge=1),
    name: str | None = Query(None, min_length=1),
    session: AsyncSession = Depends(get_session),
):
    return await get_starships(session, request, name, page)
