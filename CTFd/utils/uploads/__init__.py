import hashlib
import shutil
from pathlib import Path

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
    location = kwargs.get("location")

    # Validate location and default filename to uploaded file's name
    parent = None
    filename = file_obj.filename
    if location:
        path = Path(location)
        if len(path.parts) != 2:
            raise ValueError(
                "Location must contain two parts, a directory and a filename"
            )
        # Allow location to override the directory and filename
        parent = path.parts[0]
        filename = path.parts[1]
        location = parent + "/" + filename

    model_args = {"type": file_type, "location": location}

    model = Files
    if file_type == "challenge":
        model = ChallengeFiles
        model_args["challenge_id"] = challenge_id
    if file_type == "page":
        model = PageFiles
        model_args["page_id"] = page_id

    # Hash is calculated before upload since S3 file upload closes file object
    sha1sum = hash_file(fp=file_obj)

    uploader = get_uploader()
    location = uploader.upload(file_obj=file_obj, filename=filename, path=parent)

    model_args["location"] = location
    model_args["sha1sum"] = sha1sum

    existing_file = Files.query.filter_by(location=location).first()
    if existing_file:
        for k, v in model_args.items():
            setattr(existing_file, k, v)
        db.session.commit()
        file_row = existing_file
    else:
        file_row = model(**model_args)
        db.session.add(file_row)
        db.session.commit()
    return file_row


def hash_file(fp, algo="sha1"):
    fp.seek(0)
    if algo == "sha1":
        h = hashlib.sha1()  # nosec
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
