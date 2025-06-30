from fastapi import Request, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
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


async def get_character(character_id: int, session: AsyncSession) -> CharacterRead:
    query = (
        select(Character)
        .where(Character.id == character_id)
        .options(selectinload(Character.films), selectinload(Character.starships))
    )
    result = await session.execute(query)
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return CharacterRead.model_validate(character, from_attributes=True)
