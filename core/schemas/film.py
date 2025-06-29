from pydantic import BaseModel, ConfigDict


class FilmBase(BaseModel, extra="forbid"):
    title: str
    episode_id: int
    director: str | None
    release_date: str | None
    producer: str | None


class FilmCreate(FilmBase): ...


class FilmRead(FilmBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
