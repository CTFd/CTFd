from CTFd import create_app
from CTFd.utils import import_ctf

import zipfile
import sys

app = create_app()
with app.app_context():
    import_ctf(sys.argv[1])
