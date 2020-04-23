from CTFd.constants import RawEnum, JSEnum, JinjaEnum
from tests.helpers import create_ctfd, destroy_ctfd


def test_RawEnum():
    class Colors(str, RawEnum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert Colors.RED == "red"
    assert Colors.GREEN == "green"
    assert Colors.BLUE == "blue"
    assert sorted(Colors.keys()) == sorted(["RED", "GREEN", "BLUE"])
    assert sorted(Colors.values()) == sorted(["red", "green", "blue"])


def test_JSEnum():
    from CTFd.constants import JS_ENUMS
    import json

    @JSEnum
    class Colors(str, RawEnum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert JS_ENUMS["Colors"] == {"RED": "red", "GREEN": "green", "BLUE": "blue"}
    assert json.dumps(JS_ENUMS)


def test_JinjaEnum():
    app = create_ctfd()
    with app.app_context():

        @JinjaEnum
        class Colors(str, RawEnum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        assert app.jinja_env.globals["Colors"] is Colors
        assert app.jinja_env.globals["Colors"].RED == "red"
    destroy_ctfd(app)
