from CTFd.models import (
    Challenges,
    Comments,
    Files,
    Solves,
    Submissions,
    get_class_by_tablename,
)
from tests.helpers import create_ctfd, destroy_ctfd


def test_get_class_by_tablename():
    """
    Test that get_class_by_tablename() returns the correct table
    """
    app = create_ctfd()
    with app.app_context():
        assert get_class_by_tablename("solves") == Solves
        assert get_class_by_tablename("comments") == Comments
        assert get_class_by_tablename("files") == Files
        assert get_class_by_tablename("submissions") == Submissions
        assert get_class_by_tablename("challenges") == Challenges
    destroy_ctfd(app)


def test_build_model_filters_integer_query():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.helpers.models import build_model_filters

        filters = build_model_filters(model=Challenges, query="1", field="id")
        assert Challenges.query.filter(*filters).count() == 0

        app.db.session.add(Challenges(name="name", value=100, category="category"))
        app.db.session.commit()

        filters = build_model_filters(model=Challenges, query="1", field="id")
        assert Challenges.query.filter(*filters).count() == 1

        filters = build_model_filters(model=Challenges, query="invalid", field="id")
        assert Challenges.query.filter(*filters).count() == 0
    destroy_ctfd(app)


def test_build_model_filters_integer_extra_column_query():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.helpers.models import build_model_filters

        app.db.session.add(Challenges(name="name", value=100, category="category"))
        app.db.session.commit()

        filters = build_model_filters(
            model=Challenges,
            query="100",
            field="challenge_value",
            extra_columns={"challenge_value": Challenges.value},
        )
        assert Challenges.query.filter(*filters).count() == 1

        filters = build_model_filters(
            model=Challenges,
            query="invalid",
            field="challenge_value",
            extra_columns={"challenge_value": Challenges.value},
        )
        assert Challenges.query.filter(*filters).count() == 0
    destroy_ctfd(app)
