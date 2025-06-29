import pytest
from pydantic import ValidationError

from core.schemas.film import FilmCreate, FilmRead


def test_film_create_valid():
    data = {
        "title": "A New Hope",
        "episode_id": 4,
        "director": "George Lucas",
        "release_date": "1977-05-25",
        "producer": "Gary Kurtz",
    }

    film = FilmCreate(**data)
    assert film.title == "A New Hope"
    assert film.episode_id == 4
    assert film.director == "George Lucas"
    assert film.release_date == "1977-05-25"
    assert film.producer == "Gary Kurtz"


def test_film_create_invalid_extra_field():
    with pytest.raises(ValidationError) as exc_info:
        FilmCreate(
            title="The Empire Strikes Back",
            episode_id=5,
            director="Irvin Kershner",
            release_date="1980-05-21",
            producer="Gary Kurtz",
            unknown_field="Should fail",
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_film_create_missing_required_field():
    with pytest.raises(ValidationError) as exc_info:
        FilmCreate(episode_id=6, director="Richard Marquand")
    assert "title" in str(exc_info.value)


def test_film_read_from_model():
    # Simulate loading from DB
    db_data = {
        "id": 1,
        "title": "Return of the Jedi",
        "episode_id": 6,
        "director": "Richard Marquand",
        "release_date": "1983-05-25",
        "producer": "Howard G. Kazanjian",
    }

    film = FilmRead(**db_data)
    assert film.id == 1
    assert film.title == "Return of the Jedi"
    assert film.episode_id == 6
