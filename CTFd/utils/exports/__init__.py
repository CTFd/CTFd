import datetime
import json
import os
import re
import subprocess  # nosec B404
import sys
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import dataset
from flask import current_app as app
from flask_migrate import upgrade as migration_upgrade
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.sql import sqltypes

from CTFd import __version__ as CTFD_VERSION
from CTFd.cache import cache
from CTFd.constants.themes import DEFAULT_THEME
from CTFd.models import db, get_class_by_tablename
from CTFd.plugins import get_plugin_names
from CTFd.plugins.migrations import current as plugin_current
from CTFd.plugins.migrations import upgrade as plugin_upgrade
from CTFd.utils import get_app_config, set_config, string_types
from CTFd.utils.dates import unix_time
from CTFd.utils.exports.databases import is_database_mariadb
from CTFd.utils.exports.freeze import freeze_export
from CTFd.utils.migrations import (
    create_database,
    drop_database,
    get_available_revisions,
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
    for root, _dirs, files in os.walk(upload_folder):
        for file in files:
            parent_dir = os.path.basename(root)
            backup_zip.write(
                os.path.join(root, file),
                arcname=os.path.join("uploads", parent_dir, file),
            )

    backup_zip.close()
    backup.seek(0)
    return backup


def set_import_error(value, timeout=604800, skip_print=False):
    cache.set(key="import_error", value=value, timeout=timeout)
    if not skip_print:
        print(value)


def set_import_status(value, timeout=604800, skip_print=False):
    cache.set(key="import_status", value=value, timeout=timeout)
    if not skip_print:
        print(value)


def set_import_start_time(value, timeout=604800, skip_print=False):
    cache.set(key="import_start_time", value=value, timeout=timeout)
    if not skip_print:
        print(value)


def set_import_end_time(value, timeout=604800, skip_print=False):
    cache.set(key="import_end_time", value=value, timeout=timeout)
    if not skip_print:
        print(value)


def import_ctf(backup, erase=True):
    # Reset import cache keys and don't print these values
    set_import_error(value=None, skip_print=True)
    set_import_status(value=None, skip_print=True)

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        set_import_error(
            "Exception: Importing not currently supported for SQLite databases. See Github issue #1988."
        )
        raise Exception(
            "Importing not currently supported for SQLite databases. See Github issue #1988."
        )

    if not zipfile.is_zipfile(backup):
        set_import_error("zipfile.BadZipfile: zipfile is invalid")
        raise zipfile.BadZipfile

    backup = zipfile.ZipFile(backup)

    members = backup.namelist()
    max_content_length = get_app_config("MAX_CONTENT_LENGTH")
    for f in members:
        if f.startswith("/") or ".." in f:
            # Abort on malicious zip files
            set_import_error("zipfile.BadZipfile: zipfile is malicious")
            raise zipfile.BadZipfile
        info = backup.getinfo(f)
        if max_content_length:
            if info.file_size > max_content_length:
                set_import_error("zipfile.LargeZipFile: zipfile is too large")
                raise zipfile.LargeZipFile

    # Get list of directories in zipfile
    member_dirs = [os.path.split(m)[0] for m in members if "/" in m]
    if "db" not in member_dirs:
        set_import_error("Exception: db folder is missing")
        raise Exception(
            'CTFd couldn\'t find the "db" folder in this backup. '
            "The backup may be malformed or corrupted and the import process cannot continue."
        )

    try:
        alembic_version = json.loads(backup.open("db/alembic_version.json").read())
        alembic_version = alembic_version["results"][0]["version_num"]
    except Exception:
        set_import_error("Exception: Could not determine appropriate database version")
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
        set_import_error(
            "Exception: The version of CTFd that this backup is from is too old to be automatically imported."
        )
        raise Exception(
            "The version of CTFd that this backup is from is too old to be automatically imported."
        )

    start_time = unix_time(datetime.datetime.utcnow())

    set_import_start_time(value=start_time, skip_print=True)
    set_import_end_time(value=None, skip_print=True)

    set_import_status("started")

    sqlite = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("sqlite")
    postgres = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("postgres")
    mysql = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("mysql")
    mariadb = is_database_mariadb()

    # Only import if we can actually make it to the target migration
    if sqlite is False and alembic_version not in get_available_revisions():
        set_import_error(
            "Exception: The target migration in this backup is not available in this version of CTFd."
        )
        raise Exception(
            "The target migration in this backup is not available in this version of CTFd."
        )

    if erase:
        set_import_status("erasing")
        # Clear out existing connections to release any locks
        db.session.close()
        db.engine.dispose()

        # Kill sleeping processes on MySQL so we don't get a metadata lock
        # In my testing I didn't find that Postgres or SQLite needed the same treatment
        # Only run this when not in tests as we can't isolate the queries out
        # This is a very dirty hack. Don't try this at home kids.
        if mysql and get_app_config("TESTING", default=False) is False:
            url = make_url(get_app_config("SQLALCHEMY_DATABASE_URI"))
            r = db.session.execute("SHOW PROCESSLIST")
            processes = r.fetchall()
            for proc in processes:
                if (
                    proc.Command == "Sleep"
                    and proc.User == url.username
                    and proc.db == url.database
                ):
                    proc_id = proc.Id
                    db.session.execute(f"KILL {proc_id}")

        # Drop database and recreate it to get to a clean state
        drop_database()
        create_database()
        # We explicitly do not want to upgrade or stamp here.
        # The import will have this information.
        set_import_status("erased")

    side_db = dataset.connect(get_app_config("SQLALCHEMY_DATABASE_URI"))

    try:
        set_import_status("disabling foreign key checks")
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
        "db/topics.json",
        "db/submissions.json",
        "db/solves.json",
        "db/files.json",
        "db/notifications.json",
        "db/pages.json",
        "db/tracking.json",
        "db/config.json",
        "db/fields.json",
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
            set_import_status(f"inserting {member}")
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
                    count = len(saved["results"])
                    for i, entry in enumerate(saved["results"]):
                        set_import_status(f"inserting {member} {i}/{count}")
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

                        # From v3.1.0 to v3.5.0 FieldEntries could have been varying levels of JSON'ified strings.
                        # For example "\"test\"" vs "test". This results in issues with importing backups between
                        # databases. Specifically between MySQL and MariaDB. Because CTFd standardizes against MySQL
                        # we need to have an edge case here.
                        if member == "db/field_entries.json":
                            value = entry.get("value")
                            if value is not None:
                                try:
                                    # Attempt to convert anything to its original Python value
                                    entry["value"] = str(json.loads(value))
                                except (json.JSONDecodeError, TypeError):
                                    pass
                                finally:
                                    # Dump the value into JSON if its mariadb or skip the conversion if not mariadb
                                    if mariadb:
                                        entry["value"] = json.dumps(entry["value"])

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
                        except IntegrityError:
                            # Catch odd situation where for some reason config keys are reinserted before import completes
                            if member == "db/config.json":
                                config_id = int(entry["id"])
                                side_db.query(  # nosec B608
                                    f"DELETE FROM config WHERE id={config_id}"
                                )
                                table.insert(entry)
                            else:
                                raise

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
                            set_import_error(
                                f"Exception: Table name {table_name} contains quotes"
                            )
                            raise Exception(
                                "Table name {table_name} contains quotes".format(
                                    table_name=table_name
                                )
                            )

    # Insert data from official tables
    set_import_status("inserting tables")
    insertion(first)

    # Create tables created by plugins
    # Run plugin migrations
    set_import_status("inserting plugins")
    plugins = get_plugin_names()
    for plugin in plugins:
        set_import_status(f"inserting plugin {plugin}")
        revision = plugin_current(plugin_name=plugin)
        plugin_upgrade(plugin_name=plugin, revision=revision, lower=None)

    # Insert data for plugin tables
    insertion(members)

    # Bring plugin tables up to head revision
    plugins = get_plugin_names()
    for plugin in plugins:
        plugin_upgrade(plugin_name=plugin)

    # Extracting files
    set_import_status("uploading files")
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
    set_import_status("running head migrations")
    if sqlite:
        app.db.create_all()
        stamp_latest_revision()
    else:
        # Run migrations to bring to latest version
        migration_upgrade(revision="head")
        # Create any leftover tables, perhaps from old plugins
        app.db.create_all()

    try:
        set_import_status("reenabling foreign key checks")
        if postgres:
            side_db.query("SET session_replication_role=DEFAULT;")
        else:
            side_db.query("SET FOREIGN_KEY_CHECKS=1;")
    except Exception:
        print("Failed to enable foreign key checks. Continuing.")

    # Invalidate all cached data
    set_import_status("clearing caches")
    cache.clear()

    # Set default theme in case the current instance or the import does not provide it
    set_config("ctf_theme", DEFAULT_THEME)
    set_config("ctf_version", CTFD_VERSION)

    # Set config variables to mark import completed
    set_import_start_time(value=start_time, skip_print=True)
    set_import_end_time(value=unix_time(datetime.datetime.utcnow()), skip_print=True)


def background_import_ctf(backup):
    # Empty out import status trackers
    set_import_start_time(value=None, skip_print=True)
    set_import_end_time(value=None, skip_print=True)
    set_import_status(value=None, skip_print=True)
    set_import_error(value=None, skip_print=True)

    # The manage.py script will delete the backup for us
    f = tempfile.NamedTemporaryFile(delete=False)

    # Store the backup file in our tempfile
    backup.save(f.name)

    python = sys.executable  # Get path of Python interpreter
    manage_py = Path(app.root_path).parent / "manage.py"  # Path to manage.py
    subprocess.Popen(  # nosec B603
        [python, manage_py, "import_ctf", "--delete_import_on_finish", f.name]
    )
