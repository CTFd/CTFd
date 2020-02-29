from CTFd import create_app
from CTFd.utils import config
from CTFd.utils.exports import export_ctf

import datetime
import sys
import shutil


app = create_app()
with app.app_context():
    backup = export_ctf()

    if len(sys.argv) > 1:
        with open(sys.argv[1], "wb") as target:
            shutil.copyfileobj(backup, target)
    else:
        ctf_name = config.ctf_name()
        day = datetime.datetime.now().strftime("%Y-%m-%d")
        full_name = "{}.{}.zip".format(ctf_name, day)

        with open(full_name, "wb") as target:
            shutil.copyfileobj(backup, target)

        print("Exported {filename}".format(filename=full_name))
