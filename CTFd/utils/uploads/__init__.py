from CTFd.models import db, Files, ChallengeFiles, PageFiles
from flask import current_app as app
from werkzeug.utils import secure_filename
import hashlib
import os
import shutil

# TODO: Restructure this to use UploadSets
# TODO: Remove hashes from file paths


def upload_file(*args, **kwargs):
    file_obj = kwargs.get('file')
    challenge_id = kwargs.get('challenge_id') or kwargs.get('challenge')
    page_id = kwargs.get('page_id') or kwargs.get('page')
    file_type = kwargs.get('type', 'standard')

    model_args = {
        'type': file_type,
        'location': None,
    }

    model = Files
    if file_type == 'challenge':
        model = ChallengeFiles
        model_args['challenge_id'] = challenge_id
    if file_type == 'page':
        model = PageFiles
        model_args['page_id'] = page_id

    filename = secure_filename(file_obj.filename)

    if len(filename) <= 0:
        return False

    md5hash = hashlib.md5(os.urandom(64)).hexdigest()

    upload_folder = os.path.join(os.path.normpath(app.root_path), app.config['UPLOAD_FOLDER'])
    if not os.path.exists(os.path.join(upload_folder, md5hash)):
        os.makedirs(os.path.join(upload_folder, md5hash))

    file_obj.save(os.path.join(upload_folder, md5hash, filename))

    model_args['location'] = (md5hash + '/' + filename)

    file_row = model(**model_args)
    db.session.add(file_row)
    db.session.commit()
    return file_row


def delete_file(file_id):
    f = Files.query.filter_by(id=file_id).first_or_404()
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if os.path.exists(os.path.join(upload_folder, f.location)):  # Some kind of os.path.isfile issue on Windows...
        os.unlink(os.path.join(upload_folder, f.location))
    db.session.delete(f)
    db.session.commit()
    return True


def rmdir(directory):
    shutil.rmtree(directory, ignore_errors=True)