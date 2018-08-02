from CTFd.models import db, Files
from flask import current_app as app
from werkzeug.utils import secure_filename
import hashlib
import os
import shutil

# TODO: Restructure this to use UploadSets
# TODO: Remove hashes from file paths


def upload_file(file, chalid):
    filename = secure_filename(file.filename)

    if len(filename) <= 0:
        return False

    md5hash = hashlib.md5(os.urandom(64)).hexdigest()

    upload_folder = os.path.join(os.path.normpath(app.root_path), app.config['UPLOAD_FOLDER'])
    if not os.path.exists(os.path.join(upload_folder, md5hash)):
        os.makedirs(os.path.join(upload_folder, md5hash))

    file.save(os.path.join(upload_folder, md5hash, filename))
    db_f = Files(chalid, (md5hash + '/' + filename))
    db.session.add(db_f)
    db.session.commit()
    return db_f.id, (md5hash + '/' + filename)


def delete_file(file_id):
    f = Files.query.filter_by(id=file_id).first_or_404()
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if os.path.exists(os.path.join(upload_folder, f.location)):  # Some kind of os.path.isfile issue on Windows...
        os.unlink(os.path.join(upload_folder, f.location))
    db.session.delete(f)
    db.session.commit()
    return True


def rmdir(dir):
    shutil.rmtree(dir, ignore_errors=True)