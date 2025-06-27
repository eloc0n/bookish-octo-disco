from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models.item import Item
from core.schemas.item import ItemCreate, ItemOut


async def create_task(db: AsyncSession, item: ItemCreate) -> ItemOut:
    db_item = Item(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def get_task(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item))
    return result.scalars().all()
