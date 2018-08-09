from CTFd import create_app
from CTFd.models import *

app = create_app()

with app.app_context():
    from IPython import embed
    embed()