"""
python import.py export.zip challenges,teams,both,metadata
"""
from CTFd import create_app
from CTFd.utils import import_ctf

import sys

app = create_app()
with app.app_context():
    if len(sys.argv) == 3:
        segments = sys.argv[2].split(',')
    else:
        segments = None

    import_ctf(sys.argv[1], segments=segments)
