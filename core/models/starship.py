from core.models.character import Character
from core.models.film import Film
from core.models.links import CharacterStarshipLink, StarshipFilmLink
from sqlmodel import SQLModel, Field, Relationship


class Starship(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    model: str | None
    manufacturer: str | None

    films: list[Film] = Relationship(
        back_populates="starships", link_model=StarshipFilmLink
    )
    pilots: list[Character] = Relationship(
        back_populates="starships", link_model=CharacterStarshipLink
    )
