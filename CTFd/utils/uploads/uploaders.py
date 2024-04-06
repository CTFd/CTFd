import datetime
import os
import posixpath
import string
import time
from pathlib import Path, PurePath
from shutil import copyfileobj, rmtree
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from flask import current_app, redirect, send_file
from freezegun import freeze_time
from werkzeug.utils import safe_join, secure_filename

from CTFd.utils import get_app_config
from CTFd.utils.encoding import hexencode


class BaseUploader(object):
    def __init__(self):
        """
        Initialize the uploader with any required information
        """
        raise NotImplementedError

    def store(self, fileobj, filename):
        """
        Directly store a file object at the specified filename
        """
        raise NotImplementedError

    def upload(self, file_obj, filename):
        """
        Upload a file while handling any security protections or file renaming
        """
        raise NotImplementedError

    def download(self, filename):
        """
        Generate a Flask response to download the requested file
        """
        raise NotImplementedError

    def delete(self, filename):
        """
        Delete an uploaded file from the file store
        """
        raise NotImplementedError

    def sync(self):
        """
        Download all remotely hosted files for the purpose of exporting
        """
        raise NotImplementedError

    def open(self, mode="rb"):
        """
        Return a file pointer for an uploaded file.
        In the case of remotely hosted files, download the target file and then
        return the file pointer for the local copy.
        """
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

    def upload(self, file_obj, filename, path=None):
        if len(filename) == 0:
            raise Exception("Empty filenames cannot be used")

        # Sanitize directory name
        if path:
            path = secure_filename(path) or hexencode(os.urandom(16))
            path = path.replace(".", "")
        else:
            path = hexencode(os.urandom(16))

        # Sanitize file name
        filename = secure_filename(filename)
        file_path = posixpath.join(path, filename)

        return self.store(file_obj, file_path)

    def download(self, filename):
        return send_file(safe_join(self.base_path, filename), as_attachment=True)

    def delete(self, filename):
        if os.path.exists(os.path.join(self.base_path, filename)):
            file_path = PurePath(filename).parts[0]
            rmtree(os.path.join(self.base_path, file_path))
            return True
        return False

    def sync(self):
        pass

    def open(self, filename, mode="rb"):
        path = Path(safe_join(self.base_path, filename))
        return path.open(mode=mode)


class S3Uploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.s3 = self._get_s3_connection()
        self.bucket = get_app_config("AWS_S3_BUCKET")
        # If the custom prefix is provided, add a slash if it's missing
        custom_prefix = get_app_config("AWS_S3_CUSTOM_PREFIX")
        if custom_prefix and custom_prefix.endswith("/") is False:
            custom_prefix += "/"
        self.s3_prefix: str = custom_prefix

    def _get_s3_connection(self):
        access_key = get_app_config("AWS_ACCESS_KEY_ID")
        secret_key = get_app_config("AWS_SECRET_ACCESS_KEY")
        endpoint = get_app_config("AWS_S3_ENDPOINT_URL")
        region = get_app_config("AWS_S3_REGION")
        addressing_style = get_app_config("AWS_S3_ADDRESSING_STYLE")
        client = boto3.client(
            "s3",
            config=Config(
                signature_version="s3v4", s3={"addressing_style": addressing_style}
            ),
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint,
            region_name=region,
        )
        return client

    def _clean_filename(self, c):
        if c in string.ascii_letters + string.digits + "-" + "_" + ".":
            return True

    def store(self, fileobj, filename):
        if self.s3_prefix:
            filename = self.s3_prefix + filename
        self.s3.upload_fileobj(fileobj, self.bucket, filename)
        return filename

    def upload(self, file_obj, filename, path=None):
        # Sanitize directory name
        if path:
            path = secure_filename(path) or hexencode(os.urandom(16))
            path = path.replace(".", "")
            # Sanitize path
            path = filter(self._clean_filename, secure_filename(path).replace(" ", "_"))
            path = "".join(path)
        else:
            path = hexencode(os.urandom(16))

        # Sanitize file name
        filename = filter(
            self._clean_filename, secure_filename(filename).replace(" ", "_")
        )
        filename = "".join(filename)
        if len(filename) <= 0:
            return False

        dst = path + "/" + filename
        s3_dst = dst
        if self.s3_prefix:
            s3_dst = self.s3_prefix + dst
        self.s3.upload_fileobj(file_obj, self.bucket, s3_dst)
        return dst

    def download(self, filename):
        # S3 URLs by default are valid for one hour.
        # We round the timestamp down to the previous hour and generate the link at that time
        current_timestamp = int(time.time())
        truncated_timestamp = current_timestamp - (current_timestamp % 3600)
        if self.s3_prefix:
            filename = self.s3_prefix + filename
        key = filename
        filename = filename.split("/").pop()
        with freeze_time(datetime.datetime.utcfromtimestamp(truncated_timestamp)):
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ResponseContentDisposition": "attachment; filename={}".format(
                        filename
                    ),
                    "ResponseCacheControl": "max-age=3600",
                },
                ExpiresIn=3600,
            )

        custom_domain = get_app_config("AWS_S3_CUSTOM_DOMAIN")
        if custom_domain:
            url = urlparse(url)._replace(netloc=custom_domain).geturl()

        return redirect(url)

    def delete(self, filename):
        if self.s3_prefix:
            filename = self.s3_prefix + filename
        self.s3.delete_object(Bucket=self.bucket, Key=filename)
        return True

    def sync(self):
        local_folder = current_app.config.get("UPLOAD_FOLDER")
        # If the bucket is empty then Contents will not be in the response
        if self.s3_prefix:
            bucket_list = self.s3.list_objects(
                Bucket=self.bucket, Prefix=self.s3_prefix
            ).get("Contents", [])
        else:
            bucket_list = self.s3.list_objects(Bucket=self.bucket).get("Contents", [])

        for s3_key in bucket_list:
            s3_object = s3_key["Key"]
            # We don't want to download any directories
            if s3_object.endswith("/") is False:
                local_s3_object = s3_object
                if self.s3_prefix:
                    local_s3_object = local_s3_object.removeprefix(self.s3_prefix)
                local_path = os.path.join(local_folder, local_s3_object)
                directory = os.path.dirname(local_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                self.s3.download_file(self.bucket, s3_object, local_path)

    def open(self, filename, mode="rb"):
        local_folder = current_app.config.get("UPLOAD_FOLDER")
        local_path = os.path.join(local_folder, filename)
        self.s3.download_file(self.bucket, filename, local_path)
        return Path(local_path).open(mode=mode)
