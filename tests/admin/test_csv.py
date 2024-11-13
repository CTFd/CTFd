import io

from CTFd.models import Challenges, Flags, Hints, Teams, Users
from CTFd.utils.crypto import verify_password
from tests.helpers import create_ctfd, destroy_ctfd, gen_challenge, login_as_user


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
