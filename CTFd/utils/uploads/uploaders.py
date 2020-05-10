import os
import posixpath
import string
from shutil import copyfileobj

import boto3

from dropbox import Dropbox
from dropbox.files import FolderMetadata, WriteMode

from flask import current_app, redirect, send_file
from flask.helpers import safe_join
from werkzeug.utils import secure_filename

from CTFd.utils import get_app_config
from CTFd.utils.encoding import hexencode


class BaseUploader(object):
    def __init__(self):
        raise NotImplementedError

    def store(self, fileobj, filename):
        raise NotImplementedError

    def upload(self, file_obj, filename):
        raise NotImplementedError

    def download(self, filename):
        raise NotImplementedError

    def delete(self, filename):
        raise NotImplementedError

    def sync(self):
        raise NotImplementedError


class FilesystemUploader(BaseUploader):
    def __init__(self, base_path=None):
        super(BaseUploader, self).__init__()
        self.base_path = base_path or current_app.config.get("UPLOAD_FOLDER")

    def store(self, fileobj, filename):
        location = os.path.join(self.base_path, filename)
        directory = os.path.dirname(location)

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(location, "wb") as dst:
            copyfileobj(fileobj, dst, 16384)

        return filename

    def upload(self, file_obj, filename):
        if len(filename) == 0:
            raise Exception("Empty filenames cannot be used")

        filename = secure_filename(filename)
        md5hash = hexencode(os.urandom(16))
        file_path = posixpath.join(md5hash, filename)

        return self.store(file_obj, file_path)

    def download(self, filename):
        return send_file(safe_join(self.base_path, filename), as_attachment=True)

    def delete(self, filename):
        if os.path.exists(os.path.join(self.base_path, filename)):
            os.unlink(os.path.join(self.base_path, filename))
            return True
        return False

    def sync(self):
        pass


class S3Uploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.s3 = self._get_s3_connection()
        self.bucket = get_app_config("AWS_S3_BUCKET")

    def _get_s3_connection(self):
        access_key = get_app_config("AWS_ACCESS_KEY_ID")
        secret_key = get_app_config("AWS_SECRET_ACCESS_KEY")
        endpoint = get_app_config("AWS_S3_ENDPOINT_URL")
        client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint,
        )
        return client

    def _clean_filename(self, c):
        if c in string.ascii_letters + string.digits + "-" + "_" + ".":
            return True

    def store(self, fileobj, filename):
        self.s3.upload_fileobj(fileobj, self.bucket, filename)
        return filename

    def upload(self, file_obj, filename):
        filename = filter(
            self._clean_filename, secure_filename(filename).replace(" ", "_")
        )
        filename = "".join(filename)
        if len(filename) <= 0:
            return False

        md5hash = hexencode(os.urandom(16))

        dst = md5hash + "/" + filename
        self.s3.upload_fileobj(file_obj, self.bucket, dst)
        return dst

    def download(self, filename):
        key = filename
        filename = filename.split("/").pop()
        url = self.s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ResponseContentDisposition": "attachment; filename={}".format(
                    filename
                ),
            },
        )
        return redirect(url)

    def delete(self, filename):
        self.s3.delete_object(Bucket=self.bucket, Key=filename)
        return True

    def sync(self):
        local_folder = current_app.config.get("UPLOAD_FOLDER")
        # If the bucket is empty then Contents will not be in the response
        bucket_list = self.s3.list_objects(Bucket=self.bucket).get("Contents", [])

        for s3_key in bucket_list:
            s3_object = s3_key["Key"]
            # We don't want to download any directories
            if s3_object.endswith("/") is False:
                local_path = os.path.join(local_folder, s3_object)
                directory = os.path.dirname(local_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                self.s3.download_file(self.bucket, s3_object, local_path)


class DropboxUploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.oauth2_access_token = get_app_config("DROPBOX_OAUTH2_TOKEN")
        self.root_path = get_app_config("DROPBOX_ROOT_PATH")
        self.client = Dropbox(self.oauth2_access_token, timeout=100)
        self.write_mode = "add"  # can be overwrite

    def _clean_filename(self, c):
        if c in string.ascii_letters + string.digits + "-" + "_" + ".":
            return True

    def _full_path(self, name):
        return safe_join(self.root_path, name).replace("\\", "/")

    def store(self, fileobj, filename):
        self.client.files_upload(
            fileobj.read(), self._full_path(filename), mode=WriteMode(self.write_mode)
        )
        return filename

    def upload(self, file_obj, filename):
        filename = filter(
            self._clean_filename, secure_filename(filename).replace(" ", "_")
        )
        filename = "".join(filename)
        if len(filename) <= 0:
            return False

        md5hash = hexencode(os.urandom(16))

        dst = md5hash + "/" + filename
        self.store(file_obj, dst)
        return dst

    def download(self, filename):
        media = self.client.files_get_temporary_link(self._full_path(filename))
        print(media.link)
        return redirect(media.link)

    def delete(self, filename):
        directory = os.path.dirname(self._full_path(filename))
        self.client.files_delete(directory)
        return True

    def sync(self):
        local_folder = current_app.config.get("UPLOAD_FOLDER")

        root_metadata = self.client.files_list_folder(self.root_path)

        for folder_entry in root_metadata.entries:
            if isinstance(folder_entry, FolderMetadata):
                filemetadata = self.client.files_list_folder(folder_entry.path_lower)
                for file_entry in filemetadata.entries:
                    if not isinstance(file_entry, FolderMetadata):

                        dropbox_path = file_entry.path_lower.replace(
                            self.root_path.lower() + "/", ""
                        )
                        local_path = os.path.join(local_folder, dropbox_path)
                        directory = os.path.dirname(local_path)
                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        self.client.files_download_to_file(
                            local_path, file_entry.path_lower
                        )
