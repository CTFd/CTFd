import datetime
import json
import os
import re
import tempfile
import zipfile
from io import BytesIO

import dataset
from alembic.util import CommandError
from flask import current_app as app
from flask_migrate import upgrade as migration_upgrade
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.sql import sqltypes

from CTFd import __version__ as CTFD_VERSION
from CTFd.cache import cache
from CTFd.models import db, get_class_by_tablename
from CTFd.plugins import get_plugin_names
from CTFd.plugins.migrations import current as plugin_current
from CTFd.plugins.migrations import upgrade as plugin_upgrade
from CTFd.utils import get_app_config, set_config, string_types
from CTFd.utils.exports.freeze import freeze_export
from CTFd.utils.migrations import (
    create_database,
    drop_database,
    get_current_revision,
    stamp_latest_revision,
)
from CTFd.utils.uploads import get_uploader


def export_ctf():
    # TODO: For some unknown reason dataset is only able to see alembic_version during tests.
    # Even using a real sqlite database. This makes this test impossible to pass in sqlite.
    db = dataset.connect(get_app_config("SQLALCHEMY_DATABASE_URI"))

    # Backup database
    backup = tempfile.NamedTemporaryFile()

    backup_zip = zipfile.ZipFile(backup, "w")

    tables = db.tables
    for table in tables:
        result = db[table].all()
        result_file = BytesIO()
        freeze_export(result, fileobj=result_file)
        result_file.seek(0)
        backup_zip.writestr("db/{}.json".format(table), result_file.read())

    # # Guarantee that alembic_version is saved into the export
    if "alembic_version" not in tables:
        result = {
            "count": 1,
            "results": [{"version_num": get_current_revision()}],
            "meta": {},
        }
        result_file = BytesIO()
        json.dump(result, result_file)
        result_file.seek(0)
        backup_zip.writestr("db/alembic_version.json", result_file.read())

    # Backup uploads
    uploader = get_uploader()
    uploader.sync()

    upload_folder = os.path.join(
        os.path.normpath(app.root_path), app.config.get("UPLOAD_FOLDER")
    )
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            parent_dir = os.path.basename(root)
            backup_zip.write(
                os.path.join(root, file),
                arcname=os.path.join("uploads", parent_dir, file),
            )

    backup_zip.close()
    backup.seek(0)
    return backup


def import_ctf(backup, erase=True):
    if not zipfile.is_zipfile(backup):
        raise zipfile.BadZipfile

    backup = zipfile.ZipFile(backup)

    members = backup.namelist()
    max_content_length = get_app_config("MAX_CONTENT_LENGTH")
    for f in members:
        if f.startswith("/") or ".." in f:
            # Abort on malicious zip files
            raise zipfile.BadZipfile
        info = backup.getinfo(f)
        if max_content_length:
            if info.file_size > max_content_length:
                raise zipfile.LargeZipFile

    # Get list of directories in zipfile
    member_dirs = [os.path.split(m)[0] for m in members if "/" in m]
    if "db" not in member_dirs:
        raise Exception(
            'CTFd couldn\'t find the "db" folder in this backup. '
            "The backup may be malformed or corrupted and the import process cannot continue."
        )

    try:
        alembic_version = json.loads(backup.open("db/alembic_version.json").read())
        alembic_version = alembic_version["results"][0]["version_num"]
    except Exception:
        raise Exception(
            "Could not determine appropriate database version. This backup cannot be automatically imported."
        )

    # Check if the alembic version is from CTFd 1.x
    if alembic_version in (
        "1ec4a28fe0ff",
        "2539d8b5082e",
        "7e9efd084c5a",
        "87733981ca0e",
        "a4e30c94c360",
        "c12d2a1b0926",
        "c7225db614c1",
        "cb3cfcc47e2f",
        "cbf5620f8e15",
        "d5a224bf5862",
        "d6514ec92738",
        "dab615389702",
        "e62fd69bd417",
    ):
        raise Exception(
            "The version of CTFd that this backup is from is too old to be automatically imported."
        )

    if erase:
        # Clear out existing connections to release any locks
        db.session.close()
        db.engine.dispose()

        # Drop database and recreate it to get to a clean state
        drop_database()
        create_database()
        # We explicitly do not want to upgrade or stamp here.
        # The import will have this information.

    side_db = dataset.connect(get_app_config("SQLALCHEMY_DATABASE_URI"))
    sqlite = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("sqlite")
    postgres = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("postgres")

    try:
        if postgres:
            side_db.query("SET session_replication_role=replica;")
        else:
            side_db.query("SET FOREIGN_KEY_CHECKS=0;")
    except Exception:
        print("Failed to disable foreign key checks. Continuing.")

    first = [
        "db/teams.json",
        "db/users.json",
        "db/challenges.json",
        "db/dynamic_challenge.json",
        "db/flags.json",
        "db/hints.json",
        "db/unlocks.json",
        "db/awards.json",
        "db/tags.json",
        "db/submissions.json",
        "db/solves.json",
        "db/files.json",
        "db/notifications.json",
        "db/pages.json",
        "db/tracking.json",
        "db/config.json",
    ]

    # We want to insert certain database tables first so we are specifying
    # the order with a list. The leftover tables are tables that are from a
    # plugin (more likely) or a table where we do not care about insertion order
    for item in first:
        if item in members:
            members.remove(item)

    # Upgrade the database to the point in time that the import was taken from
    migration_upgrade(revision=alembic_version)

    members.remove("db/alembic_version.json")

    # Combine the database insertion code into a function so that we can pause
    # insertion between official database tables and plugin tables
    def insertion(table_filenames):
        for member in table_filenames:
            if member.startswith("db/"):
                table_name = member[3:-5]

                try:
                    # Try to open a file but skip if it doesn't exist.
                    data = backup.open(member).read()
                except KeyError:
                    continue

                if data:
                    table = side_db[table_name]

                    saved = json.loads(data)
                    for entry in saved["results"]:
                        # This is a hack to get SQLite to properly accept datetime values from dataset
                        # See Issue #246
                        if sqlite:
                            direct_table = get_class_by_tablename(table.name)
                            for k, v in entry.items():
                                if isinstance(v, string_types):
                                    # We only want to apply this hack to columns that are expecting a datetime object
                                    try:
                                        is_dt_column = (
                                            type(getattr(direct_table, k).type)
                                            == sqltypes.DateTime
                                        )
                                    except AttributeError:
                                        is_dt_column = False

                                    # If the table is expecting a datetime, we should check if the string is one and convert it
                                    if is_dt_column:
                                        match = re.match(
                                            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d",
                                            v,
                                        )
                                        if match:
                                            entry[k] = datetime.datetime.strptime(
                                                v, "%Y-%m-%dT%H:%M:%S.%f"
                                            )
                                            continue
                                        match = re.match(
                                            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v
                                        )
                                        if match:
                                            entry[k] = datetime.datetime.strptime(
                                                v, "%Y-%m-%dT%H:%M:%S"
                                            )
                                            continue
                        # From v2.0.0 to v2.1.0 requirements could have been a string or JSON because of a SQLAlchemy issue
                        # This is a hack to ensure we can still accept older exports. See #867
                        if member in (
                            "db/challenges.json",
                            "db/hints.json",
                            "db/awards.json",
                        ):
                            requirements = entry.get("requirements")
                            if requirements and isinstance(requirements, string_types):
                                entry["requirements"] = json.loads(requirements)

                        try:
                            table.insert(entry)
                        except ProgrammingError:
                            # MariaDB does not like JSON objects and prefers strings because it internally
                            # represents JSON with LONGTEXT.
                            # See Issue #973
                            requirements = entry.get("requirements")
                            if requirements and isinstance(requirements, dict):
                                entry["requirements"] = json.dumps(requirements)
                            table.insert(entry)

                        db.session.commit()
                    if postgres:
                        # This command is to set the next primary key ID for the re-inserted tables in Postgres. However,
                        # this command is very difficult to translate into SQLAlchemy code. Because Postgres is not
                        # officially supported, no major work will go into this functionality.
                        # https://stackoverflow.com/a/37972960
                        if '"' not in table_name and "'" not in table_name:
                            query = "SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id)+1,1), false) FROM \"{table_name}\"".format(  # nosec
                                table_name=table_name
                            )
                            side_db.engine.execute(query)
                        else:
                            raise Exception(
                                "Table name {table_name} contains quotes".format(
                                    table_name=table_name
                                )
                            )

    # Insert data from official tables
    insertion(first)

    # Create tables created by plugins
    try:
        # Run plugin migrations
        plugins = get_plugin_names()
        try:
            for plugin in plugins:
                revision = plugin_current(plugin_name=plugin)
                plugin_upgrade(plugin_name=plugin, revision=revision)
        finally:
            # Create tables that don't have migrations
            app.db.create_all()
    except OperationalError as e:
        if not postgres:
            raise e
        else:
            print("Allowing error during app.db.create_all() due to Postgres")

    # Insert data for plugin tables
    insertion(members)

    # Bring plugin tables up to head revision
    plugins = get_plugin_names()
    for plugin in plugins:
        plugin_upgrade(plugin_name=plugin)

    # Extracting files
    files = [f for f in backup.namelist() if f.startswith("uploads/")]
    uploader = get_uploader()
    for f in files:
        filename = f.split(os.sep, 1)

        if (
            len(filename) < 2 or os.path.basename(filename[1]) == ""
        ):  # just an empty uploads directory (e.g. uploads/) or any directory
            continue

        filename = filename[1]  # Get the second entry in the list (the actual filename)
        source = backup.open(f)
        uploader.store(fileobj=source, filename=filename)

    # Alembic sqlite support is lacking so we should just create_all anyway
    try:
        migration_upgrade(revision="head")
    except (OperationalError, CommandError, RuntimeError, SystemExit, Exception):
        app.db.create_all()
        stamp_latest_revision()

    try:
        if postgres:
            side_db.query("SET session_replication_role=DEFAULT;")
        else:
            side_db.query("SET FOREIGN_KEY_CHECKS=1;")
    except Exception:
        print("Failed to enable foreign key checks. Continuing.")

    # Invalidate all cached data
    cache.clear()

    # Set default theme in case the current instance or the import does not provide it
    set_config("ctf_theme", "core")
    set_config("ctf_version", CTFD_VERSION)
