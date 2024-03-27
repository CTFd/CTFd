import os
from io import BytesIO

import boto3
import pytest
from moto import mock_aws

from CTFd.utils.uploads import S3Uploader, rmdir
from tests.helpers import create_ctfd, destroy_ctfd


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def aws(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="test-region")


@pytest.fixture
def create_s3(aws):
    bucket_name = "bucket"
    boto3.client("s3").create_bucket(Bucket=bucket_name)

    return bucket_name


@mock_aws
def test_s3_uploader(create_s3):
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)


@mock_aws
def test_s3_uploader_sts(create_s3):
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_SESSION_TOKEN"] = "Jb3JpZ2luX2VjEJ///8BEK7MDNESESSIONTOKEN"
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)


@mock_aws
def test_s3_uploader_custom_prefix(create_s3):
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"
        app.config["AWS_S3_CUSTOM_PREFIX"] = "prefix"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")
        assert "fake_file.txt" in uploader.download(path).location

        fake_file2 = BytesIO("fakedfile".encode())
        path2 = uploader.upload(fake_file2, "fake_file.txt", "path")
        assert "/prefix/path/fake_file.txt" in uploader.download(path2).location
    destroy_ctfd(app)


@mock_aws
def test_s3_sync(create_s3):
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
        app.config["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        app.config["AWS_S3_BUCKET"] = bucket_name
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
