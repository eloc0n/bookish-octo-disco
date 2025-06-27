from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.session import get_db
from core.schemas.item import ItemCreate, ItemOut
from core.crud.item import create_task, get_task

router = APIRouter()


@router.post("/items/", response_model=ItemOut)
async def create(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    return await create_task(db, item)


@router.get("/items/", response_model=list[ItemOut])
async def list(db: AsyncSession = Depends(get_db)):
    return await get_task(db)
