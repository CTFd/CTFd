import random

from CTFd.models import (
    Awards,
    Challenges,
    Fails,
    Files,
    Flags,
    Hints,
    Notifications,
    Pages,
    Solves,
    Submissions,
    Tags,
    Teams,
    Tracking,
    Unlocks,
    Users,
)
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_fail,
    gen_file,
    gen_flag,
    gen_hint,
    gen_solve,
    gen_team,
    gen_tracking,
    gen_user,
    login_as_user,
)


def test_reset():
    app = create_ctfd()
    with app.app_context():
        base_user = "user"

        for x in range(10):
            chal = gen_challenge(app.db, name="chal_name{}".format(x))
            gen_flag(app.db, challenge_id=chal.id, content="flag")
            gen_hint(app.db, challenge_id=chal.id)
            gen_file(
                app.db,
                location="{name}/{name}.file".format(name=chal.name),
                challenge_id=chal.id,
            )

        for x in range(10):
            user = base_user + str(x)
            user_email = user + "@examplectf.com"
            user_obj = gen_user(app.db, name=user, email=user_email)
            gen_award(app.db, user_id=user_obj.id)
            gen_solve(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_fail(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_tracking(app.db, user_id=user_obj.id)

        # Add PageFiles
        for x in range(5):
            gen_file(
                app.db,
                location="page_file{name}/page_file{name}.file".format(name=x),
                page_id=1,
            )

        assert Users.query.count() == 11  # 11 because of the first admin user
        assert Challenges.query.count() == 10
        assert (
            Files.query.count() == 15
        )  # This should be 11 because ChallengeFiles=10 and PageFiles=5
        assert Flags.query.count() == 10
        assert Hints.query.count() == 10
        assert Submissions.query.count() == 20
        assert Pages.query.count() == 1
        assert Tracking.query.count() == 10

        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "pages": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Pages.query.count() == 0
        assert Users.query.count() == 11
        assert Challenges.query.count() == 10
        assert Tracking.query.count() == 11
        assert Files.query.count() == 10

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "notifications": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Notifications.query.count() == 0
        assert Users.query.count() == 11
        assert Challenges.query.count() == 10
        assert Tracking.query.count() == 11

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "challenges": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Challenges.query.count() == 0
        assert Flags.query.count() == 0
        assert Hints.query.count() == 0
        assert Files.query.count() == 0
        assert Tags.query.count() == 0
        assert Users.query.count() == 11
        assert Tracking.query.count() == 11

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "submissions": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Submissions.query.count() == 0
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Awards.query.count() == 0
        assert Unlocks.query.count() == 0
        assert Users.query.count() == 11
        assert Challenges.query.count() == 0
        assert Flags.query.count() == 0
        assert Tracking.query.count() == 0

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "accounts": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/setup")
        assert Users.query.count() == 0
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
            gen_hint(app.db, challenge_id=chal.id)
            gen_file(
                app.db,
                location="{name}/{name}.file".format(name=chal.name),
                challenge_id=chal.id,
            )

        for x in range(10):
            user = base_user + str(x)
            user_email = user + "@examplectf.com"
            user_obj = gen_user(app.db, name=user, email=user_email)
            team_obj = gen_team(
                app.db,
                name=base_team + str(x),
                email=base_team + str(x) + "@examplectf.com",
            )
            team_obj.members.append(user_obj)
            team_obj.captain_id = user_obj.id
            app.db.session.commit()
            gen_award(app.db, user_id=user_obj.id)
            gen_solve(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_fail(app.db, user_id=user_obj.id, challenge_id=random.randint(1, 10))
            gen_tracking(app.db, user_id=user_obj.id)

        # Add PageFiles
        for x in range(5):
            gen_file(
                app.db,
                location="page_file{name}/page_file{name}.file".format(name=x),
                page_id=1,
            )

        assert Teams.query.count() == 10
        # 10 random users, 40 users (10 teams * 4), 1 admin user
        assert Users.query.count() == 51
        assert Challenges.query.count() == 10
        assert (
            Files.query.count() == 15
        )  # This should be 11 because ChallengeFiles=10 and PageFiles=5
        assert Flags.query.count() == 10
        assert Hints.query.count() == 10
        assert Submissions.query.count() == 20
        assert Solves.query.count() == 10
        assert Fails.query.count() == 10
        assert Tracking.query.count() == 10

        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "pages": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Pages.query.count() == 0
        assert Teams.query.count() == 10
        assert Users.query.count() == 51
        assert Challenges.query.count() == 10
        assert Tracking.query.count() == 11
        assert Files.query.count() == 10

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "notifications": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Notifications.query.count() == 0
        assert Teams.query.count() == 10
        assert Users.query.count() == 51
        assert Challenges.query.count() == 10
        assert Tracking.query.count() == 11

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "challenges": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Challenges.query.count() == 0
        assert Flags.query.count() == 0
        assert Hints.query.count() == 0
        assert Files.query.count() == 0
        assert Tags.query.count() == 0
        assert Teams.query.count() == 10
        assert Users.query.count() == 51
        assert Tracking.query.count() == 11

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "submissions": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Submissions.query.count() == 0
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Awards.query.count() == 0
        assert Unlocks.query.count() == 0
        assert Teams.query.count() == 10
        assert Users.query.count() == 51
        assert Challenges.query.count() == 0
        assert Flags.query.count() == 0
        assert Tracking.query.count() == 0

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "accounts": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/setup")
        assert Users.query.count() == 0
        assert Teams.query.count() == 0
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0
        assert Tracking.query.count() == 0
    destroy_ctfd(app)
