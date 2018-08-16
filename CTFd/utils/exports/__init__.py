from CTFd.utils import get_app_config, get_config, set_config
from CTFd.models import db, Pages, Teams, Challenges
from datafreeze.format import SERIALIZERS
from flask import current_app as app
from datafreeze.format.fjson import JSONSerializer, JSONEncoder
import dataset
import datafreeze
import datetime
import json
import os
import re
import six
import shutil
import zipfile


class CTFdSerializer(JSONSerializer):
    """
    Slightly modified datafreeze serializer so that we can properly
    export the CTFd database into a zip file.
    """

    def close(self):
        for path, result in self.buckets.items():
            result = self.wrap(result)

            if self.fileobj is None:
                fh = open(path, 'wb')
            else:
                fh = self.fileobj

            data = json.dumps(result,
                              cls=JSONEncoder,
                              indent=self.export.get_int('indent'))

            callback = self.export.get('callback')
            if callback:
                data = "%s && %s(%s);" % (callback, callback, data)

            if six.PY3:
                fh.write(bytes(data, encoding='utf-8'))
            else:
                fh.write(data)
            if self.fileobj is None:
                fh.close()


# SERIALIZERS['ctfd'] = CTFdSerializer  # Load the custom serializer


def export_ctf(segments=None):
    db = dataset.connect(get_app_config('SQLALCHEMY_DATABASE_URI'))
    if segments is None:
        segments = ['challenges', 'teams', 'both', 'metadata']

    groups = {
        'challenges': [
            'challenges',
            'files',
            'tags',
            'keys',
            'hints',
        ],
        'teams': [
            'teams',
            'tracking',
            'awards',
        ],
        'both': [
            'solves',
            'wrong_keys',
            'unlocks',
        ],
        'metadata': [
            'alembic_version',
            'config',
            'pages',
        ]
    }

    # Backup database
    backup = six.BytesIO()

    backup_zip = zipfile.ZipFile(backup, 'w')

    # TODO: Sqlite has very little alembic support. We should fake out an alembic version.

    tables = db.tables
    for table in tables:
        result = db[table].all()
        result_file = six.BytesIO()
        datafreeze.freeze(result, format='json', fileobj=result_file)
        result_file.seek(0)
        backup_zip.writestr('db/{}.json'.format(table), result_file.read())

    # TODO: Reimplement partial exports

    # for segment in segments:
    #     group = groups[segment]
    #     for item in group:
    #         result = db[item].all()
    #         result_file = six.BytesIO()
    #         datafreeze.freeze(result, format='ctfd', fileobj=result_file)
    #         result_file.seek(0)
    #         backup_zip.writestr('db/{}.json'.format(item), result_file.read())
    #
    # # Guarantee that alembic_version is saved into the export
    # if 'metadata' not in segments:
    #     result = db['alembic_version'].all()
    #     result_file = six.BytesIO()
    #     datafreeze.freeze(result, format='ctfd', fileobj=result_file)
    #     result_file.seek(0)
    #     backup_zip.writestr('db/alembic_version.json', result_file.read())

    # Backup uploads
    upload_folder = os.path.join(os.path.normpath(app.root_path), app.config.get('UPLOAD_FOLDER'))
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            parent_dir = os.path.basename(root)
            backup_zip.write(os.path.join(root, file), arcname=os.path.join('uploads', parent_dir, file))

    backup_zip.close()
    backup.seek(0)
    return backup


def import_ctf(backup, segments=None, erase=False):
    side_db = dataset.connect(get_app_config('SQLALCHEMY_DATABASE_URI'))
    if segments is None:
        segments = ['challenges', 'teams', 'both', 'metadata']

    if not zipfile.is_zipfile(backup):
        raise zipfile.BadZipfile

    backup = zipfile.ZipFile(backup)

    members = backup.namelist()
    max_content_length = get_app_config('MAX_CONTENT_LENGTH')
    for f in members:
        if f.startswith('/') or '..' in f:
            # Abort on malicious zip files
            raise zipfile.BadZipfile
        info = backup.getinfo(f)
        if max_content_length:
            if info.file_size > max_content_length:
                raise zipfile.LargeZipFile

    groups = {
        'challenges': [
            'challenges',
            'files',
            'tags',
            'keys',
            'hints',
        ],
        'teams': [
            'teams',
            'tracking',
            'awards',
        ],
        'both': [
            'solves',
            'wrong_keys',
            'unlocks',
        ],
        'metadata': [
            'alembic_version',
            'config',
            'pages',
        ]
    }

    # Need special handling of metadata
    if 'metadata' in segments:
        meta = groups['metadata']
        segments.remove('metadata')
        meta.remove('alembic_version')

        for item in meta:
            table = side_db[item]
            path = "db/{}.json".format(item)
            data = backup.open(path).read()

            # Some JSON files will be empty
            if data:
                if item == 'config':
                    saved = json.loads(data)
                    for entry in saved['results']:
                        key = entry['key']
                        value = entry['value']
                        set_config(key, value)

                elif item == 'pages':
                    saved = json.loads(data)
                    for entry in saved['results']:
                        # Support migration c12d2a1b0926_add_draft_and_title_to_pages
                        route = entry['route']
                        title = entry.get('title', route.title())
                        html = entry['html']
                        draft = entry.get('draft', False)
                        auth_required = entry.get('auth_required', False)
                        page = Pages.query.filter_by(route=route).first()
                        if page:
                            page.html = html
                        else:
                            page = Pages(title, route, html, draft=draft, auth_required=auth_required)
                            db.session.add(page)
                        db.session.commit()

    teams_base = db.session.query(db.func.max(Teams.id)).scalar() or 0
    chals_base = db.session.query(db.func.max(Challenges.id)).scalar() or 0

    for segment in segments:
        group = groups[segment]
        for item in group:
            table = side_db[item]
            path = "db/{}.json".format(item)
            data = backup.open(path).read()
            if data:
                saved = json.loads(data)
                for entry in saved['results']:
                    entry_id = entry.pop('id', None)
                    # This is a hack to get SQlite to properly accept datetime values from dataset
                    # See Issue #246
                    if get_app_config('SQLALCHEMY_DATABASE_URI').startswith('sqlite'):
                        for k, v in entry.items():
                            if isinstance(v, six.string_types):
                                match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d", v)
                                if match:
                                    entry[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
                                    continue
                                match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v)
                                if match:
                                    entry[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                                    continue
                    for k, v in entry.items():
                        if k == 'chal' or k == 'chalid':
                            if entry[k]:
                                entry[k] += chals_base
                        if k == 'team' or k == 'teamid':
                            if entry[k]:
                                entry[k] += teams_base

                    if item == 'teams':
                        table.insert_ignore(entry, ['email'])
                    elif item == 'keys':
                        # Support migration 2539d8b5082e_rename_key_type_to_type
                        key_type = entry.get('key_type', None)
                        if key_type is not None:
                            entry['type'] = key_type
                            del entry['key_type']
                        table.insert(entry)
                    else:
                        table.insert(entry)
            else:
                continue

    # Extracting files
    files = [f for f in backup.namelist() if f.startswith('uploads/')]
    upload_folder = app.config.get('UPLOAD_FOLDER')
    for f in files:
        filename = f.split(os.sep, 1)

        if len(filename) < 2:  # just an empty uploads directory (e.g. uploads/)
            continue

        filename = filename[1]  # Get the second entry in the list (the actual filename)
        full_path = os.path.join(upload_folder, filename)
        dirname = os.path.dirname(full_path)

        # Create any parent directories for the file
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        source = backup.open(f)
        target = open(full_path, "wb")
        with source, target:
            shutil.copyfileobj(source, target)
