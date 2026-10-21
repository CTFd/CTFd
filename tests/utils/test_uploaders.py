import os
import tempfile
from io import BytesIO
from unittest.mock import patch

import boto3
import pytest
from moto import mock_s3

from CTFd.utils.uploads import rmdir
from CTFd.utils.uploads.uploaders import FilesystemUploader, S3Uploader
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


@mock_s3
def test_s3_uploader_open_cannot_write_outside_upload_folder():
    """A key that resolves outside UPLOAD_FOLDER must not be written to disk"""
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

        sandbox = tempfile.mkdtemp(prefix="ctfd-s3-open-escape-")
        try:
            escape_dir = os.path.join(sandbox, "nested")
            escape_target = os.path.join(escape_dir, "escaped.txt")
            uploader = S3Uploader()
            uploader.store(BytesIO(b"escaped"), escape_target)

            with pytest.raises(ValueError):
                uploader.open(escape_target)

            assert os.path.exists(escape_target) is False, escape_target
            assert os.path.exists(escape_dir) is False, escape_dir
        finally:
            rmdir(sandbox)
    destroy_ctfd(app)


@mock_s3
def test_s3_sync_skips_keys_outside_upload_folder():
    """sync must not write objects whose key escapes UPLOAD_FOLDER"""
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

        sandbox = tempfile.mkdtemp(prefix="ctfd-s3-sync-escape-")
        try:
            escape_dir = os.path.join(sandbox, "nested")
            escape_target = os.path.join(escape_dir, "escaped.txt")
            uploader = S3Uploader()
            uploader.store(BytesIO(b"escaped"), escape_target)
            good = uploader.upload(BytesIO(b"contents"), "fake_file.txt")

            uploader.sync()

            assert os.path.exists(escape_target) is False, escape_target
            assert os.path.exists(escape_dir) is False, escape_dir

            local_good = os.path.join(app.config["UPLOAD_FOLDER"], good)
            try:
                assert os.path.exists(local_good) is True, (
                    "sync stopped syncing safe keys"
                )
            finally:
                rmdir(os.path.dirname(local_good))
        finally:
            rmdir(sandbox)
    destroy_ctfd(app)


def test_filesystem_uploader_store_cannot_write_outside_base_path():
    """A filename that resolves outside base_path must not be written"""
    app = create_ctfd()
    with app.app_context():
        base_root = tempfile.mkdtemp(prefix="ctfd-fs-base-")
        base = os.path.join(base_root, "var", "lib", "ctfd", "uploads")
        os.makedirs(base)
        sandbox = tempfile.mkdtemp(prefix="ctfd-fs-escape-")
        try:
            uploader = FilesystemUploader(base_path=base)
            escape_dir = os.path.join(sandbox, "nested")
            escape_target = os.path.join(escape_dir, "escaped.txt")

            for filename in (
                escape_target,
                os.path.relpath(escape_target, base),
                "seed/" + os.path.relpath(escape_target, base),
            ):
                with pytest.raises(ValueError):
                    uploader.store(BytesIO(b"escaped"), filename)
                with pytest.raises(ValueError):
                    uploader.open(filename)
                assert os.path.exists(escape_target) is False, filename
                assert os.path.exists(escape_dir) is False, filename

            # a normal filename still stores and reads back
            uploader.store(BytesIO(b"contents"), "dir/handout.txt")
            with uploader.open("dir/handout.txt") as fp:
                assert fp.read() == b"contents"
        finally:
            rmdir(sandbox)
            rmdir(base_root)
    destroy_ctfd(app)


def test_filesystem_uploader_delete_stays_inside_base_path():
    """delete must not remove a tree outside base_path."""
    app = create_ctfd()
    with app.app_context():
        base_root = tempfile.mkdtemp(prefix="ctfd-fs-base-")
        base = os.path.join(base_root, "var", "lib", "ctfd", "uploads")
        os.makedirs(base)
        victim = tempfile.mkdtemp(prefix="ctfd-fs-victim-")
        try:
            uploader = FilesystemUploader(base_path=base)
            keepsake = os.path.join(victim, "keep.txt")
            with open(keepsake, "wb") as fp:
                fp.write(b"not an upload")

            with patch("CTFd.utils.uploads.uploaders.rmtree") as fake_rmtree:
                for location in (
                    keepsake,
                    os.path.relpath(keepsake, base),
                    os.path.join("..", os.path.basename(base)),
                    "/",
                    "..",
                ):
                    assert uploader.delete(location) is False, location
                    assert fake_rmtree.called is False, (
                        f"{location!r} reached rmtree with "
                        f"{fake_rmtree.call_args_list!r}"
                    )
            assert os.path.exists(keepsake) is True
            assert os.path.exists(base) is True

            # a real upload is still deleted, directory and all
            uploader.store(BytesIO(b"contents"), "dir/handout.txt")
            assert uploader.delete("dir/handout.txt") is True
            assert os.path.exists(os.path.join(base, "dir")) is False
        finally:
            rmdir(victim)
            rmdir(base_root)
    destroy_ctfd(app)
