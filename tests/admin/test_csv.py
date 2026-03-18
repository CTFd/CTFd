import csv
import io

from CTFd.models import Challenges, Flags, Hints, Teams, Users
from CTFd.utils.crypto import verify_password
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_team,
    gen_user,
    login_as_user,
)


def test_export_csv_works():
    """Test that CSV exports work properly"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        client = login_as_user(app, name="admin", password="password")

        csv_data = client.get("/admin/export/csv?table=challenges").get_data(
            as_text=True
        )
        assert len(csv_data) > 0

    destroy_ctfd(app)


def test_import_csv_works():
    """Test that CSV imports work properly"""
    USERS_CSV = b"""name,email,password
user1,user1@examplectf.com,password
user2,user2@examplectf.com,password"""

    TEAMS_CSV = b"""name,email,password
team1,team1@examplectf.com,password
team2,team2@examplectf.com,password"""

    CHALLENGES_CSV = b'''name,category,description,value,flags,tags,hints
challenge1,category1,description1,100,"flag1,flag2,flag3","tag1,tag2,tag3","hint1,hint2,hint3"'''

    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "csv_type": "users",
                "csv_file": (io.BytesIO(USERS_CSV), "users.csv"),
                "nonce": sess.get("nonce"),
            }

        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")
        assert Users.query.count() == 3
        user = Users.query.filter_by(id=2).first()
        assert user.name == "user1"
        assert user.email == "user1@examplectf.com"
        assert verify_password("password", user.password)
        user = Users.query.filter_by(id=3).first()
        assert user.name == "user2"
        assert user.email == "user2@examplectf.com"
        assert verify_password("password", user.password)

        with client.session_transaction() as sess:
            data = {
                "csv_type": "teams",
                "csv_file": (io.BytesIO(TEAMS_CSV), "users.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")
        assert Teams.query.count() == 2
        team = Teams.query.filter_by(id=1).first()
        assert team.name == "team1"
        assert team.email == "team1@examplectf.com"
        assert verify_password("password", team.password)
        team = Teams.query.filter_by(id=2).first()
        assert team.name == "team2"
        assert team.email == "team2@examplectf.com"
        assert verify_password("password", team.password)

        with client.session_transaction() as sess:
            data = {
                "csv_type": "challenges",
                "csv_file": (io.BytesIO(CHALLENGES_CSV), "challenges.csv"),
                "nonce": sess.get("nonce"),
            }

        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")
        assert Challenges.query.count() == 1
        challenge = Challenges.query.filter_by(id=1).first()
        assert challenge.name == "challenge1"
        assert challenge.category == "category1"
        assert challenge.description == "description1"
        assert challenge.value == 100
        assert len(challenge.flags) == 3
        assert len(challenge.tags) == 3
        assert len(challenge.hints) == 3

    destroy_ctfd(app)


def test_import_challenge_csv_with_json():

    CHALLENGES_CSV = b'''name,category,description,value,flags,tags,hints
challenge1,category1,description1,100,"[{""type"": ""static"", ""content"": ""flag1"", ""data"": ""case_insensitive""}, {""type"": ""regex"", ""content"": ""(.*)"", ""data"": ""case_insensitive""}, {""type"": ""static"", ""content"": ""flag3""}]","tag1,tag2,tag3","[{""content"": ""hint1"", ""cost"": 10}, {""content"": ""hint2"", ""cost"": 20}, {""content"": ""hint3"", ""cost"": 30}]"'''

    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "csv_type": "challenges",
                "csv_file": (io.BytesIO(CHALLENGES_CSV), "challenges.csv"),
                "nonce": sess.get("nonce"),
            }

        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")
        assert Challenges.query.count() == 1
        challenge = Challenges.query.filter_by(id=1).first()
        assert challenge.name == "challenge1"
        assert challenge.category == "category1"
        assert challenge.description == "description1"
        assert challenge.value == 100
        assert len(challenge.flags) == 3
        assert len(challenge.tags) == 3
        assert len(challenge.hints) == 3

        for i in range(1, 4):
            h = Hints.query.filter_by(id=i).first()
            assert h.cost == i * 10
            assert h.content == f"hint{i}"

        f = Flags.query.filter_by(id=1).first()
        assert f.type == "static"
        assert f.content == "flag1"
        assert f.data == "case_insensitive"

        f = Flags.query.filter_by(id=2).first()
        assert f.type == "regex"
        assert f.content == "(.*)"
        assert f.data == "case_insensitive"

        f = Flags.query.filter_by(id=3).first()
        assert f.type == "static"
        assert f.content == "flag3"
        assert f.data is None

    destroy_ctfd(app)


def test_export_users_teams_csv():
    """users+teams export has all expected columns including team_captain"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db, name="team1", email="team1@examplectf.com", member_count=2)
        client = login_as_user(app, name="admin", password="password")

        csv_data = client.get("/admin/export/csv?table=users%2Bteams").get_data(
            as_text=True
        )
        assert len(csv_data) > 0
        lines = [l for l in csv_data.splitlines() if l]  # noqa: E741
        header = lines[0].split(",")
        for col in (
            "name",
            "email",
            "password",
            "team_name",
            "team_email",
            "team_password",
            "team_captain",
        ):
            assert col in header
        # Each user should have their own row (admin + 2 team members)
        assert len(lines) >= 3

    destroy_ctfd(app)


def test_import_users_teams_csv_assigns_existing_team():
    """Import assigns new users to a pre-existing team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team = Teams(name="alpha", email="alpha@examplectf.com", password="password")
        app.db.session.add(team)
        app.db.session.commit()
        team_id = team.id

        CSV = (
            b"name,email,password,team_name,team_email,team_password\n"
            b"user1,user1@examplectf.com,password,alpha,alpha@examplectf.com,\n"
            b"user2,user2@examplectf.com,password,alpha,alpha@examplectf.com,"
        )
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "users_teams.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")

        assert (
            Users.query.filter_by(email="user1@examplectf.com").first().team_id
            == team_id
        )
        assert (
            Users.query.filter_by(email="user2@examplectf.com").first().team_id
            == team_id
        )

    destroy_ctfd(app)


def test_import_users_teams_csv_creates_new_team():
    """Import creates a team when it doesn't exist yet"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = b"name,email,password,team_name,team_email,team_password\nuser1,user1@examplectf.com,password,newteam,newteam@examplectf.com,teampass"
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "users_teams.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")

        team = Teams.query.filter_by(name="newteam").first()
        assert team is not None
        assert team.email == "newteam@examplectf.com"
        assert (
            Users.query.filter_by(email="user1@examplectf.com").first().team_id
            == team.id
        )

    destroy_ctfd(app)


def test_import_users_teams_csv_creates_new_user():
    """Import creates a user that doesn't exist yet"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = b"name,email,password,team_name,team_email,team_password\nnewuser,newuser@examplectf.com,password,squad,squad@examplectf.com,teampass"
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "users_teams.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")

        user = Users.query.filter_by(email="newuser@examplectf.com").first()
        assert user is not None
        assert user.name == "newuser"
        assert verify_password("password", user.password)
        team = Teams.query.filter_by(name="squad").first()
        assert team is not None
        assert user.team_id == team.id

    destroy_ctfd(app)


def test_import_users_teams_csv_team_captain():
    """Import sets the team captain when team_captain column is true"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = (
            b"name,email,password,team_name,team_email,team_password,team_captain\n"
            b"cap,cap@examplectf.com,password,crew,crew@examplectf.com,teampass,true\n"
            b"member,member@examplectf.com,password,crew,crew@examplectf.com,,false"
        )
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "users_teams.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")

        team = Teams.query.filter_by(name="crew").first()
        cap = Users.query.filter_by(email="cap@examplectf.com").first()
        member = Users.query.filter_by(email="member@examplectf.com").first()
        assert team is not None
        assert team.captain_id == cap.id
        assert member.team_id == team.id

    destroy_ctfd(app)


def test_export_users_teams_csv_user_without_team():
    """Users with no team assignment export with empty team columns"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="loner", email="loner@examplectf.com")
        client = login_as_user(app, name="admin", password="password")

        csv_data = client.get("/admin/export/csv?table=users%2Bteams").get_data(
            as_text=True
        )
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        loner = next(r for r in rows if r["email"] == "loner@examplectf.com")
        assert loner["team_name"] == ""
        assert loner["team_email"] == ""
        assert loner["team_captain"] == ""

    destroy_ctfd(app)


def test_import_users_teams_csv_empty_team_name_leaves_unassigned():
    """Row with no team_name leaves the user unassigned and does not count as an error"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = b"name,email,password,team_name,team_email,team_password\nsolo,solo@examplectf.com,password,,,"
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "ut.csv"),
                "nonce": sess.get("nonce"),
            }
        resp = client.post(
            "/admin/import/csv", data=data, content_type="multipart/form-data"
        )
        # No errors — should redirect (302)
        assert resp.status_code == 302
        user = Users.query.filter_by(email="solo@examplectf.com").first()
        assert user.team_id is None

    destroy_ctfd(app)


def test_import_users_teams_csv_missing_email_skipped_others_proceed():
    """Rows with a missing email are skipped; other valid rows are still processed"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = (
            b"name,email,password,team_name,team_email,team_password\n"
            b"nomail,,,,gamma@examplectf.com,\n"
            b"real,real@examplectf.com,password,gamma,gamma@examplectf.com,teampass"
        )
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "ut.csv"),
                "nonce": sess.get("nonce"),
            }
        resp = client.post(
            "/admin/import/csv", data=data, content_type="multipart/form-data"
        )
        # There were errors (missing email) so we get a 500 with error details
        assert resp.status_code == 500

        # The valid row was still committed
        team = Teams.query.filter_by(name="gamma").first()
        assert team is not None
        real = Users.query.filter_by(email="real@examplectf.com").first()
        assert real.team_id == team.id

    destroy_ctfd(app)


def test_import_users_teams_csv_new_user_email_creates_user():
    """Rows with an email not in the DB create a new user and proceed"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = (
            b"name,email,password,team_name,team_email,team_password\n"
            b"ghost,ghost@examplectf.com,password,gamma,gamma@examplectf.com,teampass"
        )
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "ut.csv"),
                "nonce": sess.get("nonce"),
            }
        resp = client.post(
            "/admin/import/csv", data=data, content_type="multipart/form-data"
        )
        assert resp.status_code == 302

        ghost = Users.query.filter_by(email="ghost@examplectf.com").first()
        assert ghost is not None
        assert ghost.name == "ghost"
        team = Teams.query.filter_by(name="gamma").first()
        assert team is not None
        assert ghost.team_id == team.id

    destroy_ctfd(app)


def test_import_users_teams_csv_same_team_not_duplicated():
    """Multiple rows referencing the same team name reuse the existing team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        CSV = (
            b"name,email,password,team_name,team_email,team_password\n"
            b"u1,u1@examplectf.com,password,delta,delta@examplectf.com,teampass\n"
            b"u2,u2@examplectf.com,password,delta,delta@examplectf.com,\n"
            b"u3,u3@examplectf.com,password,delta,delta@examplectf.com,"
        )
        client = login_as_user(app, name="admin", password="password")
        with client.session_transaction() as sess:
            data = {
                "csv_type": "users+teams",
                "csv_file": (io.BytesIO(CSV), "ut.csv"),
                "nonce": sess.get("nonce"),
            }
        client.post("/admin/import/csv", data=data, content_type="multipart/form-data")

        assert Teams.query.filter_by(name="delta").count() == 1
        team = Teams.query.filter_by(name="delta").first()
        for email in ("u1@examplectf.com", "u2@examplectf.com", "u3@examplectf.com"):
            assert Users.query.filter_by(email=email).first().team_id == team.id

    destroy_ctfd(app)
