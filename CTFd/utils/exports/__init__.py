from CTFd.utils import get_app_config, set_config
from CTFd.utils.migrations import get_current_revision, create_database, drop_database, stamp_latest_revision
from CTFd.utils.uploads import get_uploader
from CTFd.models import db
from CTFd.cache import cache
from datafreeze.format import SERIALIZERS
from flask import current_app as app
from flask_migrate import upgrade
from datafreeze.format.fjson import JSONSerializer, JSONEncoder
from sqlalchemy.exc import OperationalError, ProgrammingError
from alembic.util import CommandError
import dataset
import datafreeze
import datetime
import json
import os
import re
import six
import zipfile
import tempfile


class CTFdSerializer(JSONSerializer):
    """
    Slightly modified datafreeze serializer so that we can properly
    export the CTFd database into a zip file.
    """

    def close(self):
        for path, result in self.buckets.items():
            result = self.wrap(result)

            if self.fileobj is None:
                fh = open(path, "wb")
            else:
                fh = self.fileobj

            # Certain databases (MariaDB) store JSON as LONGTEXT.
            # Before emitting a file we should standardize to valid JSON (i.e. a dict)
            # See Issue #973
            for i, r in enumerate(result["results"]):
                data = r.get("requirements")
                if data:
                    try:
                        if isinstance(data, six.string_types):
                            result["results"][i]["requirements"] = json.loads(data)
                    except ValueError:
                        pass

            data = json.dumps(
                result, cls=JSONEncoder, indent=self.export.get_int("indent")
            )

            callback = self.export.get("callback")
            if callback:
                data = "%s && %s(%s);" % (callback, callback, data)

            if six.PY3:
                fh.write(bytes(data, encoding="utf-8"))
            else:
                fh.write(data)
            if self.fileobj is None:
                fh.close()


SERIALIZERS["ctfd"] = CTFdSerializer  # Load the custom serializer


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
        result_file = six.BytesIO()
        datafreeze.freeze(result, format="ctfd", fileobj=result_file)
        result_file.seek(0)
        backup_zip.writestr("db/{}.json".format(table), result_file.read())

    # # Guarantee that alembic_version is saved into the export
    if "alembic_version" not in tables:
        result = {
            "count": 1,
            "results": [{"version_num": get_current_revision()}],
            "meta": {},
        }
        result_file = six.BytesIO()
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

    if erase:
        drop_database()
        create_database()
        # We explicitly do not want to upgrade or stamp here.
        # The import will have this information.

    side_db = dataset.connect(get_app_config("SQLALCHEMY_DATABASE_URI"))
    sqlite = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("sqlite")
    postgres = get_app_config("SQLALCHEMY_DATABASE_URI").startswith("postgres")

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

    for item in first:
        if item in members:
            members.remove(item)

    members = first + members

    alembic_version = json.loads(backup.open("db/alembic_version.json").read())[
        "results"
    ][0]["version_num"]
    upgrade(revision=alembic_version)

    # Create tables created by plugins
    try:
        app.db.create_all()
    except OperationalError as e:
        if not postgres:
            raise e
        else:
            print("Allowing error during app.db.create_all() due to Postgres")

    members.remove("db/alembic_version.json")

    for member in members:
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
                        for k, v in entry.items():
                            if isinstance(v, six.string_types):
                                match = re.match(
                                    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d", v
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
                        if requirements and isinstance(requirements, six.string_types):
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

    # Extracting files
    files = [f for f in backup.namelist() if f.startswith("uploads/")]
    uploader = get_uploader()
    for f in files:
        filename = f.split(os.sep, 1)

        if len(filename) < 2:  # just an empty uploads directory (e.g. uploads/)
            continue

        filename = filename[1]  # Get the second entry in the list (the actual filename)
        source = backup.open(f)
        uploader.store(fileobj=source, filename=filename)

    # Alembic sqlite support is lacking so we should just create_all anyway
    try:
        upgrade(revision="head")
    except (CommandError, RuntimeError, SystemExit):
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
