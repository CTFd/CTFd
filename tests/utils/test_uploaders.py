import os
from io import BytesIO

import boto3
from moto import mock_s3

from CTFd.utils.uploads import S3Uploader, rmdir
from tests.helpers import create_ctfd, destroy_ctfd


@mock_s3
def test_s3_uploader():
    conn = boto3.resource("s3", region_name="test-region")
    conn.create_bucket(
        Bucket="bucket", CreateBucketConfiguration={"LocationConstraint": "test-region"}
    )

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = "bucket"
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == "bucket"

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)


@mock_s3
def test_s3_uploader_custom_prefix():
    conn = boto3.resource("s3", region_name="test-region")
    conn.create_bucket(
        Bucket="bucket", CreateBucketConfiguration={"LocationConstraint": "test-region"}
    )

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = "bucket"
        app.config["AWS_S3_REGION"] = "test-region"
        app.config["AWS_S3_CUSTOM_PREFIX"] = "prefix"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == "bucket"

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")
        assert "fake_file.txt" in uploader.download(path).location

        fake_file2 = BytesIO("fakedfile".encode())
        path2 = uploader.upload(fake_file2, "fake_file.txt", "path")
        assert "/prefix/path/fake_file.txt" in uploader.download(path2).location
    destroy_ctfd(app)


@mock_s3
def test_s3_sync():
    conn = boto3.resource("s3", region_name="test-region")
    conn.create_bucket(
        Bucket="bucket", CreateBucketConfiguration={"LocationConstraint": "test-region"}
    )

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = "bucket"
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()
        uploader.sync()

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")
        full_path = os.path.join(app.config["UPLOAD_FOLDER"], path)

        try:
            uploader.sync()
            with open(full_path) as f:
                assert f.read() == "fakedfile"
        finally:
            rmdir(os.path.dirname(full_path))
    destroy_ctfd(app)
