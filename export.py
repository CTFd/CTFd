from CTFd import create_app
from CTFd.utils import config
from CTFd.utils.exports import export_ctf

import datetime
import sys
import shutil


app = create_app()
with app.app_context():
    print(
        "This file will be deleted in CTFd v4.0. Switch to using `python manage.py export_ctf`"
    )
    backup = export_ctf()

    if len(sys.argv) > 1:
        with open(sys.argv[1], "wb") as target:
            shutil.copyfileobj(backup, target)
    else:
        ctf_name = config.ctf_name()
        day = datetime.datetime.now().strftime("%Y-%m-%d_%T")
        full_name = "{}.{}.zip".format(ctf_name, day)

        with open(full_name, "wb") as target:
            shutil.copyfileobj(backup, target)

        print("Exported {filename}".format(filename=full_name))
