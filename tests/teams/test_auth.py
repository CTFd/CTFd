from CTFd.models import Teams
from CTFd.utils import set_config, get_config
from freezegun import freeze_time
from tests.helpers import *
from mock import patch


def test_banned_team():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db, banned=True)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        db.session.commit()

        client = login_as_user(app)

        routes = ['/', '/challenges', '/api/v1/challenges']
        for route in routes:
            r = client.get(route)
            assert r.status_code == 403
    destroy_ctfd(app)
