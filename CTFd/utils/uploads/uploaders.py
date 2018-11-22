from CTFd.utils import string_types, get_app_config
from flask import current_app, send_file, redirect
from flask.helpers import safe_join
from werkzeug.utils import secure_filename
from shutil import copyfileobj
import hashlib
import os
import boto3
import string


class BaseUploader(object):
    def __init__(self):
        raise NotImplementedError

    def upload(self, file_obj, filename):
        raise NotImplementedError

    def download(self, filename):
        raise NotImplementedError

    def delete(self, filename):
        raise NotImplementedError


class FilesystemUploader(BaseUploader):
    def __init__(self, base_path=None):
        super(BaseUploader, self).__init__()
        self.base_path = base_path or current_app.config.get('UPLOAD_FOLDER')

    def upload(self, file_obj, filename):
        if len(filename) == 0:
            raise Exception('Empty filenames cannot be used')

        filename = secure_filename(filename)
        md5hash = hashlib.md5(os.urandom(64)).hexdigest()

        if not os.path.exists(os.path.join(self.base_path, md5hash)):
            os.makedirs(os.path.join(self.base_path, md5hash))

        location = os.path.join(self.base_path, md5hash, filename)

        dst_file = open(location, 'wb')
        try:
            copyfileobj(file_obj, dst_file, 16384)
        finally:
            dst_file.close()

        key = os.path.join(md5hash, filename)
        return key

    def download(self, filename):
        return send_file(safe_join(self.base_path, filename))

    def delete(self, filename):
        if os.path.exists(os.path.join(self.base_path, filename)):
            os.unlink(os.path.join(self.base_path, filename))
            return True
        return False


class S3Uploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.s3 = self._get_s3_connection()
        self.bucket = get_app_config('AWS_S3_BUCKET')

    def _get_s3_connection(self):
        access_key = get_app_config('AWS_ACCESS_KEY_ID')
        secret_key = get_app_config('AWS_SECRET_ACCESS_KEY')
        endpoint = get_app_config('AWS_S3_ENDPOINT_URL')
        client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint
        )
        return client

    def _clean_filename(self, c):
        if c in string.ascii_letters + string.digits + '-' + '_' + '.':
            return True

    def upload(self, file_obj, filename):
        filename = filter(self._clean_filename, secure_filename(filename).replace(' ', '_'))
        if len(filename) <= 0:
            return False

        md5hash = hashlib.md5(os.urandom(64)).hexdigest()

        dst = md5hash + '/' + filename
        self.s3.upload_fileobj(file_obj, self.bucket, dst)
        return dst

    def download(self, filename):
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': filename
            }
        )
        return redirect(url)

    def delete(self, filename):
        self.s3.delete_object(Bucket=self.bucket, Key=filename)
        return True
