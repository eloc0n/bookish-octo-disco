from pydantic import BaseModel, ConfigDict


class StarshipBase(BaseModel, extra="forbid"):
    name: str
    model: str | None = None
    manufacturer: str | None = None


class StarshipCreate(StarshipBase): ...


class StarshipRead(StarshipBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
