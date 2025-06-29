import pytest
from pydantic import ValidationError
from core.schemas.starship import StarshipCreate, StarshipRead


def test_starship_create_valid():
    data = {
        "name": "Millennium Falcon",
        "model": "YT-1300",
        "manufacturer": "Corellian Engineering Corporation",
    }
    starship = StarshipCreate(**data)

    assert starship.name == "Millennium Falcon"
    assert starship.model == "YT-1300"
    assert starship.manufacturer == "Corellian Engineering Corporation"


def test_starship_create_missing_optional_fields():
    data = {
        "name": "X-Wing",
    }
    starship = StarshipCreate(**data)

    assert starship.name == "X-Wing"
    assert starship.model is None
    assert starship.manufacturer is None


def test_starship_create_extra_field_raises_error():
    data = {
        "name": "TIE Fighter",
        "model": "Twin Ion Engine",
        "manufacturer": "Sienar Fleet Systems",
        "speed": "fast",  # Invalid extra field
    }
    with pytest.raises(ValidationError) as exc:
        StarshipCreate(**data)

    assert "Extra inputs are not permitted" in str(exc.value)


def test_starship_read_model_config_from_attributes():
    class DummyStarship:
        def __init__(self):
            self.id = 42
            self.name = "Slave I"
            self.model = "Firespray-31"
            self.manufacturer = "Kuat Systems Engineering"

    dummy = DummyStarship()
    schema = StarshipRead.model_validate(dummy, from_attributes=True)

    assert schema.id == 42
    assert schema.name == "Slave I"
    assert schema.model == "Firespray-31"
