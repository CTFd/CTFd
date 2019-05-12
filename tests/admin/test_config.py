from CTFd.models import Users, Teams, Challenges, Fails, Solves, Tracking
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    register_user,
    login_as_user,
    gen_challenge,
    gen_award,
    gen_flag,
    gen_user,
    gen_team,
    gen_solve,
    gen_fail,
    gen_tracking,
)
import random


def test_reset():
    app = create_ctfd()
    with app.app_context():
        base_user = "user"

        for x in range(10):
            chal = gen_challenge(app.db, name="chal_name{}".format(x))
            gen_flag(app.db, challenge_id=chal.id, content="flag")

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
            data = {"nonce": sess.get("nonce")}
            client.post("/admin/reset", data=data)

        assert Users.query.count() == 0
        assert Challenges.query.count() == 10
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Tracking.query.count() == 0
    destroy_ctfd(app)


def test_reset_team_mode():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        base_user = "user"
        base_team = "team"

        for x in range(10):
            chal = gen_challenge(app.db, name="chal_name{}".format(x))
            gen_flag(app.db, challenge_id=chal.id, content="flag")

        for x in range(10):
            user = base_user + str(x)
            user_email = user + "@ctfd.io"
            user_obj = gen_user(app.db, name=user, email=user_email)
            team_obj = gen_team(
                app.db, name=base_team + str(x), email=base_team + str(x) + "@ctfd.io"
            )
            team_obj.members.append(user_obj)
            team_obj.captain_id = user_obj.id
            app.db.session.commit()
            gen_award(app.db, user_id=user_obj.id)
            gen_solve(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_fail(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_tracking(app.db, user_id=user_obj.id)

        assert Teams.query.count() == 10
        assert (
            Users.query.count() == 51
        )  # 10 random users, 40 users (10 teams * 4), 1 admin user
        assert Challenges.query.count() == 10

        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce")}
            client.post("/admin/reset", data=data)

        assert Teams.query.count() == 0
        assert Users.query.count() == 0
        assert Challenges.query.count() == 10
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Tracking.query.count() == 0
    destroy_ctfd(app)
