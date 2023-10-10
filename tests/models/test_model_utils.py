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
