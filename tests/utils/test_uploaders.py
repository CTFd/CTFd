import os

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import boto3
from moto import mock_s3
from six import BytesIO

from CTFd.utils.uploads import S3Uploader, rmdir
from tests.helpers import create_ctfd, destroy_ctfd


@mock_s3
def test_s3_uploader():
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="bucket")

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = "bucket"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == "bucket"

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)


@mock_s3
def test_s3_sync():
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="bucket")

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = "bucket"

        uploader = S3Uploader()
        uploader.sync()

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")
        full_path = Path(app.config["UPLOAD_FOLDER"]).joinpath(path)

        try:
            uploader.sync()
            with full_path.open() as f:
                assert f.read() == "fakedfile"
        finally:
            full_path.rmdir()
    destroy_ctfd(app)
