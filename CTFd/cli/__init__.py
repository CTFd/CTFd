import datetime
import shutil
from pathlib import Path

import click
from flask import Blueprint, current_app

from CTFd.utils import get_config as get_config_util
from CTFd.utils import set_config as set_config_util
from CTFd.utils.config import ctf_name
from CTFd.utils.exports import export_ctf as export_ctf_util
from CTFd.utils.exports import import_ctf as import_ctf_util
from CTFd.utils.exports import set_import_end_time, set_import_error

_cli = Blueprint("cli", __name__)


def jsenums():
    import json
    import os

    from CTFd.constants import JS_ENUMS

    path = os.path.join(current_app.root_path, "themes/core/assets/js/constants.js")

    with open(path, "w+") as f:
        for k, v in JS_ENUMS.items():
            f.write("const {} = Object.freeze({});".format(k, json.dumps(v)))


BUILD_COMMANDS = {"jsenums": jsenums}


@_cli.cli.command("get_config")
@click.argument("key")
def get_config(key):
    print(get_config_util(key))


@_cli.cli.command("set_config")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    print(set_config_util(key, value).value)


@_cli.cli.command("build")
@click.argument("cmd")
def build(cmd):
    cmd = BUILD_COMMANDS.get(cmd)
    cmd()


@_cli.cli.command("export_ctf")
@click.argument("path", default="")
def export_ctf(path):
    backup = export_ctf_util()

    if path:
        with open(path, "wb") as target:
            shutil.copyfileobj(backup, target)
    else:
        name = ctf_name()
        day = datetime.datetime.now().strftime("%Y-%m-%d_%T")
        full_name = f"{name}.{day}.zip"

        with open(full_name, "wb") as target:
            shutil.copyfileobj(backup, target)

        print(f"Exported {full_name}")


@_cli.cli.command("import_ctf")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--delete_import_on_finish",
    default=False,
    is_flag=True,
    help="Delete import file when import is finished",
)
def import_ctf(path, delete_import_on_finish=False):
    try:
        import_ctf_util(path)
    except Exception as e:
        from CTFd.utils.dates import unix_time

        set_import_error("Import Failure: " + str(e))
        set_import_end_time(value=unix_time(datetime.datetime.utcnow()))

    if delete_import_on_finish:
        print(f"Deleting {path}")
        Path(path).unlink()
