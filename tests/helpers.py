from CTFd import create_app
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.engine.url import make_url


def create_ctfd(ctf_name="CTFd", name="admin", email="admin@ctfd.io", password="password"):
    app = create_app('CTFd.config.TestingConfig')

    url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if url.drivername == 'postgres':
        url.drivername = 'postgresql'

    if database_exists(url):
        drop_database(url)
        create_database(url)
        with app.app_context():
            app.db.create_all()

    with app.app_context():
        with app.test_client() as client:
            data = {}
            r = client.get('/setup')  # Populate session with nonce
            with client.session_transaction() as sess:
                data = {
                    "ctf_name": ctf_name,
                    "name": name,
                    "email": email,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/setup', data=data)
    return app


def register_user(app, name="user", email="user@ctfd.io", password="password"):
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/register')
            with client.session_transaction() as sess:
                data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/register', data=data)


def login_as_user(app, name="user", password="password"):
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/login')
            with client.session_transaction() as sess:
                data = {
                    "name": name,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/login', data=data)
            return client