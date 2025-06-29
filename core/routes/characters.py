from fastapi import APIRouter, Depends, Query, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database.session import get_session
from core.schemas import CharacterRead
from core.crud.character import get_characters
from core.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/", response_model=PaginatedResponse[CharacterRead])
async def characters(
    request: Request,
    page: int = Query(1, ge=1),
    name: str | None = Query(None, min_length=1),
    session: AsyncSession = Depends(get_session),
):
    return await get_characters(session, request, name, page)
