from typing import TYPE_CHECKING
from .links import CharacterStarshipLink, CharacterFilmLink
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    # Verbose workaround to F821 Undefined name `Film` etc...
    # When running ruff formatter
    from .film import Film
    from .starship import Starship


class Character(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    gender: str | None
    birth_year: str | None

    films: list["Film"] = Relationship(
        back_populates="characters", link_model=CharacterFilmLink
    )
    starships: list["Starship"] = Relationship(
        back_populates="pilots", link_model=CharacterStarshipLink
    )
