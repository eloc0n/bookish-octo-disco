from typing import TYPE_CHECKING
from .links import CharacterFilmLink, StarshipFilmLink
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    # Verbose workaround to F821 Undefined name `Character` etc...
    # When running ruff formatter
    from .character import Character
    from .starship import Starship


class Film(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    episode_id: int | None
    director: str | None
    producer: str | None
    release_date: str | None

    characters: list["Character"] = Relationship(
        back_populates="films", link_model=CharacterFilmLink
    )
    starships: list["Starship"] = Relationship(
        back_populates="films", link_model=StarshipFilmLink
    )
