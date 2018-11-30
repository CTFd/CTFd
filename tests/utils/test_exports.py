# -*- coding: utf-8 -*-
from tests.helpers import *
from CTFd.utils.exports import import_ctf, export_ctf
import os


def test_export_ctf():
    """Test that CTFd can export the database"""
    app = create_ctfd()
    if not app.config.get('SQLALCHEMY_DATABASE_URI').startswith('sqlite'):
        with app.app_context():
            register_user(app)
            chal = gen_challenge(app.db, name=text_type('🐺'))
            chal_id = chal.id
            hint = gen_hint(app.db, chal_id)

            client = login_as_user(app)
            with client.session_transaction() as sess:
                data = {
                    "target": 1,
                    "type": "hints"
                }
            r = client.post('/api/v1/unlocks', json=data)
            output = r.get_data(as_text=True)
            output = json.loads(output)
            app.db.session.commit()
            backup = export_ctf()

            with open('export.zip', 'wb') as f:
                f.write(backup.read())
            os.remove('export.zip')
    destroy_ctfd(app)


def test_import_ctf():
    """Test that CTFd can import a CTF"""
    app = create_ctfd()
    if not app.config.get('SQLALCHEMY_DATABASE_URI').startswith('sqlite'):
        with app.app_context():
            base_user = 'user'
            for x in range(10):
                user = base_user + str(x)
                user_email = user + "@ctfd.io"
                gen_user(app.db, name=user, email=user_email)

            for x in range(10):
                chal = gen_challenge(app.db, name='chal_name{}'.format(x))
                gen_flag(app.db, challenge_id=chal.id, content='flag')

            app.db.session.commit()

            backup = export_ctf()

            with open('export.zip', 'wb') as f:
                f.write(backup.read())
    destroy_ctfd(app)

    app = create_ctfd()
    # TODO: These databases should work but they don't...
    if not app.config.get('SQLALCHEMY_DATABASE_URI').startswith('sqlite'):
        with app.app_context():
            import_ctf('export.zip')

            if not app.config.get('SQLALCHEMY_DATABASE_URI').startswith('postgres'):
                # TODO: Dig deeper into why Postgres fails here
                assert Users.query.count() == 11
                assert Challenges.query.count() == 10
                assert Flags.query.count() == 10
    destroy_ctfd(app)
