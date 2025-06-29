from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from core.models import Character
from core.schemas.character import CharacterRead
from core.schemas.pagination import PaginatedResponse
from core.crud.utils.pagination import Paginator

paginator = Paginator(limit=20)


async def get_characters(
    session: AsyncSession, request: Request, name: str | None = None, page: int = 1
) -> PaginatedResponse:
    return await paginator.paginate(
        request=request,
        session=session,
        model=Character,
        schema=CharacterRead,
        page=page,
        filter=name,
        filter_field=Character.name,
        options=[selectinload(Character.films), selectinload(Character.starships)],
    )
