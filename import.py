"""
python import.py export.zip
"""
from CTFd import create_app
from CTFd.utils.exports import import_ctf

import sys

app = create_app()
with app.app_context():
    import_ctf(sys.argv[1])
