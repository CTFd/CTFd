# -*- coding: utf-8 -*-
import json
import os
import zipfile

from CTFd.models import Challenges, Flags, Teams, Users
from CTFd.utils import text_type
from CTFd.utils.exports import export_ctf, import_ctf
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_hint,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
)


def test_export_ctf():
    """Test that CTFd can export the database"""
    app = create_ctfd()
    if not app.config.get("SQLALCHEMY_DATABASE_URI").startswith("sqlite"):
        with app.app_context():
            register_user(app)
            chal1 = gen_challenge(app.db, name=text_type("🐺"))
            gen_challenge(
                app.db, name=text_type("🐺"), requirements={"prerequisites": [1]}
            )
            chal_id = chal1.id
            gen_hint(app.db, chal_id)

            client = login_as_user(app)
            with client.session_transaction():
                data = {"target": 1, "type": "hints"}
            r = client.post("/api/v1/unlocks", json=data)
            output = r.get_data(as_text=True)
            json.loads(output)
            app.db.session.commit()
            backup = export_ctf()

            with open("export.test_export_ctf.zip", "wb") as f:
                f.write(backup.read())

            export = zipfile.ZipFile("export.test_export_ctf.zip", "r")
            data = json.loads(export.read("db/challenges.json"))
            assert data["results"][1]["requirements"] == {"prerequisites": [1]}

            os.remove("export.test_export_ctf.zip")
    destroy_ctfd(app)


def test_import_ctf():
    """Test that CTFd can import a CTF"""
    app = create_ctfd()
    if not app.config.get("SQLALCHEMY_DATABASE_URI").startswith("sqlite"):
        with app.app_context():
            base_user = "user"
            for x in range(10):
                user = base_user + str(x)
                user_email = user + "@examplectf.com"
                gen_user(app.db, name=user, email=user_email)

            base_team = "team"
            for x in range(5):
                team = base_team + str(x)
                team_email = team + "@examplectf.com"
                gen_team(app.db, name=team, email=team_email)

            for x in range(9):
                chal = gen_challenge(app.db, name="chal_name{}".format(x))
                gen_flag(app.db, challenge_id=chal.id, content="flag")

            chal = gen_challenge(
                app.db, name="chal_name10", requirements={"prerequisites": [1]}
            )
            gen_flag(app.db, challenge_id=chal.id, content="flag")

            app.db.session.commit()

            backup = export_ctf()

            with open("export.test_import_ctf.zip", "wb") as f:
                f.write(backup.read())
    destroy_ctfd(app)

    app = create_ctfd()
    # TODO: These databases should work but they don't...
    if not app.config.get("SQLALCHEMY_DATABASE_URI").startswith("sqlite"):
        with app.app_context():
            import_ctf("export.test_import_ctf.zip")

            if not app.config.get("SQLALCHEMY_DATABASE_URI").startswith("postgres"):
                # TODO: Dig deeper into why Postgres fails here
                assert Users.query.count() == 31
                assert Teams.query.count() == 5
                assert Challenges.query.count() == 10
                assert Flags.query.count() == 10

                chal = Challenges.query.filter_by(name="chal_name10").first()
                assert chal.requirements == {"prerequisites": [1]}
    destroy_ctfd(app)
