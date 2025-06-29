from sqlmodel import SQLModel, Field


class CharacterFilmLink(SQLModel, table=True):
    character_id: int | None = Field(
        default=None, foreign_key="character.id", primary_key=True
    )
    film_id: int | None = Field(default=None, foreign_key="film.id", primary_key=True)


class StarshipFilmLink(SQLModel, table=True):
    starship_id: int | None = Field(
        default=None, foreign_key="starship.id", primary_key=True
    )
    film_id: int | None = Field(default=None, foreign_key="film.id", primary_key=True)


class CharacterStarshipLink(SQLModel, table=True):
    character_id: int | None = Field(
        default=None, foreign_key="character.id", primary_key=True
    )
    starship_id: int | None = Field(
        default=None, foreign_key="starship.id", primary_key=True
    )
