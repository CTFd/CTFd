from CTFd.models import Teams
from CTFd.utils.scores import get_standings, get_team_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_team,
    gen_user,
    login_as_user,
)


def setup_app(app):
    user1 = gen_user(app.db, name="user1", email="user1@examplectf.com")
    team1 = gen_team(app.db, name="team1", email="team1@examplectf.com")
    user1.team_id = team1.id
    team1.members.append(user1)
    team1.hidden = True

    user2 = gen_user(app.db, name="user2", email="user2@examplectf.com")
    team2 = gen_team(app.db, name="team2", email="team2@examplectf.com")
    user2.team_id = team2.id
    team2.members.append(user2)

    gen_challenge(app.db)
    gen_flag(app.db, 1)

    app.db.session.commit()

    with login_as_user(app, name="user1") as client:
        flag = {"challenge_id": 1, "submission": "flag"}
        client.post("/api/v1/challenges/attempt", json=flag)

    with login_as_user(app, name="user2") as client:
        flag = {"challenge_id": 1, "submission": "flag"}
        client.post("/api/v1/challenges/attempt", json=flag)


def test_standings():
    app = create_ctfd(user_mode="teams")

    with app.app_context():
        setup_app(app)

        standings = get_standings()

        assert standings[0].name == "team2"
        assert standings[0].score == 100

    destroy_ctfd(app)


def test_team_standings():
    app = create_ctfd(user_mode="teams")

    with app.app_context():
        setup_app(app)

        team_standings = get_team_standings()

        first_team = Teams.query.filter_by(id=team_standings[0].team_id).first_or_404()

        assert first_team.name == "team2"
        assert first_team.score == 100


def test_admin_standings():
    app = create_ctfd(user_mode="teams")

    with app.app_context():
        setup_app(app)

        standings = get_standings(admin=True)

        assert standings[0].name == "team1"
        assert standings[0].score == 100


def test_admin_team_standings():
    app = create_ctfd(user_mode="teams")

    with app.app_context():
        setup_app(app)

        team_standings = get_team_standings(admin=True)

        first_team = Teams.query.filter_by(id=team_standings[0].team_id).first_or_404()

        assert first_team.name == "team1"
        assert first_team.score == 100
