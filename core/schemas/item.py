from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemOut(ItemCreate):
    id: int

    model_config = {"from_attributes": True}
