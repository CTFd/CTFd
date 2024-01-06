import hashlib
import shutil

from CTFd.models import ChallengeFiles, Files, PageFiles, db
from CTFd.utils import get_app_config
from CTFd.utils.uploads.uploaders import FilesystemUploader, S3Uploader

UPLOADERS = {"filesystem": FilesystemUploader, "s3": S3Uploader}


def get_uploader():
    return UPLOADERS.get(get_app_config("UPLOAD_PROVIDER") or "filesystem")()


def upload_file(*args, **kwargs):
    file_obj = kwargs.get("file")
    challenge_id = kwargs.get("challenge_id") or kwargs.get("challenge")
    page_id = kwargs.get("page_id") or kwargs.get("page")
    file_type = kwargs.get("type", "standard")

    model_args = {"type": file_type, "location": None}

    model = Files
    if file_type == "challenge":
        model = ChallengeFiles
        model_args["challenge_id"] = challenge_id
    if file_type == "page":
        model = PageFiles
        model_args["page_id"] = page_id

    uploader = get_uploader()
    location = uploader.upload(file_obj=file_obj, filename=file_obj.filename)

    sha1sum = hash_file(fp=file_obj)

    model_args["location"] = location
    model_args["sha1sum"] = sha1sum

    file_row = model(**model_args)
    db.session.add(file_row)
    db.session.commit()
    return file_row


def hash_file(fp, algo="sha1"):
    fp.seek(0)
    if algo == "sha1":
        h = hashlib.sha1()
        # https://stackoverflow.com/a/64730457
        while chunk := fp.read(1024):
            h.update(chunk)
        fp.seek(0)
        return h.hexdigest()
    else:
        raise NotImplementedError


def delete_file(file_id):
    f = Files.query.filter_by(id=file_id).first_or_404()

    uploader = get_uploader()
    uploader.delete(filename=f.location)

    db.session.delete(f)
    db.session.commit()
    return True


def rmdir(directory):
    shutil.rmtree(directory, ignore_errors=True)
