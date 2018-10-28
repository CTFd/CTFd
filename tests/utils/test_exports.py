from tests.helpers import *
from CTFd.utils.exports import import_ctf, export_ctf
import os


def test_export_ctf():
    """Test that CTFd can properly export the database"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db, name=text_type('🐺'))
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        app.db.session.commit()
        backup = export_ctf()

        with open('export.zip', 'wb') as f:
            f.write(backup.getvalue())
        os.remove('export.zip')
    destroy_ctfd(app)


def test_import_ctf():
    """Test that CTFd can import a CTF"""
    app = create_ctfd()
    # TODO: Unrelated to an in-memory database, imports in a test environment are not working with SQLite...
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite') is False:
        with app.app_context():
            base_user = 'user'
            for x in range(10):
                user = base_user + str(x)
                user_email = user + "@ctfd.io"
                gen_team(app.db, name=user, email=user_email)

            for x in range(10):
                chal = gen_challenge(app.db, name='chal_name{}'.format(x))
                gen_flag(app.db, challenge_id=chal.id, flag='flag')

            app.db.session.commit()

            backup = export_ctf()

            with open('export.zip', 'wb') as f:
                f.write(backup.read())
        destroy_ctfd(app)

        app = create_ctfd()
        with app.app_context():
            import_ctf('export.zip')

            app.db.session.commit()

            print(Teams.query.count())
            print(Challenges.query.count())

            assert Teams.query.count() == 11
            assert Challenges.query.count() == 10
            assert Flags.query.count() == 10
    destroy_ctfd(app)