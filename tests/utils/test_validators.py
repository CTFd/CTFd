from CTFd.utils.validators import validate_country_code
from marshmallow import ValidationError


def test_validate_country_code():
    assert validate_country_code("") is None
    # TODO: This looks poor, when everything moves to pytest we should remove exception catches like this.
    try:
        validate_country_code("ZZ")
    except ValidationError:
        pass
