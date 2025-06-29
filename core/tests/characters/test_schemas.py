import pytest
from pydantic import ValidationError
from core.schemas.character import CharacterCreate, CharacterRead


def test_character_schema_rejects_extra_field():
    with pytest.raises(ValidationError):
        CharacterRead(
            id=1,
            name="Obi-Wan Kenobi",
            gender="male",
            birth_year="57BBY",
            films=[],
            starships=[],
            rank="Donut Master",  # Unexpected field
        )


def test_character_read_schema_validation():
    data = {
        "id": 1,
        "name": "Luke Skywalker",
        "gender": "male",
        "birth_year": "19BBY",
        "films": [
            {
                "id": 10,
                "title": "A New Hope",
                "director": "John Lucas",
                "producer": "Josh Lucas",
                "episode_id": 1,
                "release_date": "1977-05-25",
            }
        ],
        "starships": [
            {"id": 5, "name": "X-Wing", "model": "T-65B", "manufacturer": "A sith lord"}
        ],
    }

    character = CharacterRead(**data)

    assert character.name == "Luke Skywalker"
    assert character.films[0].title == "A New Hope"
    assert character.starships[0].name == "X-Wing"


def test_character_create_and_read_roundtrip():
    character_data = {"name": "Leia Organa", "gender": "female", "birth_year": "19BBY"}

    create = CharacterCreate(**character_data)
    assert create.name == "Leia Organa"

    read_data = {**character_data, "id": 2, "films": [], "starships": []}
    read = CharacterRead(**read_data)
    assert read.id == 2
