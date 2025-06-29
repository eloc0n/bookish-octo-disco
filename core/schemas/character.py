from core.schemas.film import FilmRead
from core.schemas.starship import StarshipRead
from pydantic import BaseModel, ConfigDict


class CharacterBase(BaseModel, extra="forbid"):
    name: str
    gender: str | None
    birth_year: str | None


class CharacterCreate(CharacterBase): ...


class CharacterRead(CharacterBase):
    id: int
    films: list[FilmRead] = []
    starships: list[StarshipRead] = []

    model_config = ConfigDict(from_attributes=True)
