from CTFd.models import Users, Challenges
from tests.helpers import *
import random


def test_get_admin_config():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/config')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_reset():
    app = create_ctfd()
    with app.app_context():
        base_user = 'user'

        for x in range(10):
            chal = gen_challenge(app.db, name='chal_name{}'.format(x))
            gen_flag(app.db, challenge_id=chal.id, content='flag')

        for x in range(10):
            user = base_user + str(x)
            user_email = user + "@ctfd.io"
            user_obj = gen_user(app.db, name=user, email=user_email)
            gen_award(app.db, user_id=user_obj.id)
            gen_solve(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_fail(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_tracking(app.db, user_id=user_obj.id)

        assert Users.query.count() == 11  # 11 because of the first admin user
        assert Challenges.query.count() == 10

        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
            r = client.post('/admin/reset', data=data)

        assert Users.query.count() == 0
        assert Challenges.query.count() == 10
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Tracking.query.count() == 0
    destroy_ctfd(app)
