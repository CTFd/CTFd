import os
from io import BytesIO
import json

import boto3
from botocore.exceptions import ClientError
import pytest
from moto import mock_aws
from moto.core import set_initial_no_auth_action_count

from CTFd.utils.uploads import S3Uploader, rmdir
from tests.helpers import create_ctfd, destroy_ctfd


@pytest.fixture(scope="function")
def aws():
    with mock_aws():
        yield boto3.client("s3", region_name="test-region")

@pytest.fixture
def create_s3(aws):
    bucket_name = "bucket"
    boto3.client("s3").create_bucket(Bucket=bucket_name)

    return bucket_name

@pytest.fixture(scope="function")
@mock_aws
def create_access_key():
    user_name = "ctfd-user"
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
            {"Effect": "Allow", "Action": "sts:GetSessionToken", "Resource": "*"}
        ],
    }
    iam = boto3.client("iam", region_name="test-region")
    iam.create_user(UserName=user_name)
    iam.put_user_policy(
        UserName = user_name,
        PolicyName= "test-policy",
        PolicyDocument = json.dumps(policy_document)
    )

    access_key = iam.create_access_key(UserName=user_name)["AccessKey"]

    return access_key

@pytest.fixture(scope="function")
@mock_aws
def create_session_token():
    role_name = "ctfd-role"
    session_name = "ctfd-session"
    assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    })
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
            {"Effect": "Allow", "Action": "sts:GetSessionToken", "Resource": "*"}
        ],
    }
    iam = boto3.client("iam", region_name="test-region")
    role = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
    )
    iam.put_role_policy(
        RoleName = role_name,
        PolicyName= "test-policy",
        PolicyDocument = json.dumps(policy_document)
    )

    sts = boto3.client('sts', region_name="test-region")

    session_token = sts.assume_role(
        RoleArn=role['Role']['Arn'],
        RoleSessionName=session_name
    )

    return session_token["Credentials"]

@pytest.fixture(scope="function")
@mock_aws
def create_access_key_with_invalid_policy():
    user_name = "ctfd-user"
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Deny", "Action": "*", "Resource": "*"}],
    }
    iam = boto3.client("iam", region_name="test-region")
    iam.create_user(UserName=user_name)
    iam.put_user_policy(
        UserName = user_name,
        PolicyName= "test-policy",
        PolicyDocument = json.dumps(policy_document)
    )

    access_key = iam.create_access_key(UserName=user_name)["AccessKey"]

    return access_key


@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_uploader(create_s3, create_access_key):
    access_key = create_access_key
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = access_key["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = access_key["SecretAccessKey"]
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)

@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_uploader_sts(create_s3, create_access_key, create_session_token):
    session_token = create_session_token
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = session_token["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = session_token["SecretAccessKey"]
        app.config["AWS_SESSION_TOKEN"] = session_token["SessionToken"]
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        path = uploader.upload(fake_file, "fake_file.txt")

        assert "fake_file.txt" in uploader.download(path).location
    destroy_ctfd(app)

@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_uploader_custom_prefix(create_s3, create_access_key):
    access_key = create_access_key
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = access_key["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = access_key["SecretAccessKey"]
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


@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_uploader_custom_prefix_sts(create_s3, create_access_key, create_session_token):
    session_token = create_session_token
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = session_token["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = session_token["SecretAccessKey"]
        app.config["AWS_SESSION_TOKEN"] = session_token["SessionToken"]
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

@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_sync(create_s3, create_access_key):
    access_key = create_access_key
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = access_key["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = access_key["SecretAccessKey"]
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


@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_sync_sts(create_s3, create_access_key, create_session_token):
    session_token = create_session_token
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = session_token["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = session_token["SecretAccessKey"]
        app.config["AWS_SESSION_TOKEN"] = session_token["SessionToken"]
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

@set_initial_no_auth_action_count(0)
@mock_aws
def test_s3_uploader_failure(create_s3, create_access_key_with_invalid_policy):
    access_key = create_access_key_with_invalid_policy
    bucket_name = create_s3

    app = create_ctfd()
    with app.app_context():
        app.config["UPLOAD_PROVIDER"] = "s3"
        app.config["AWS_ACCESS_KEY_ID"] = access_key["AccessKeyId"]
        app.config["AWS_SECRET_ACCESS_KEY"] = access_key["SecretAccessKey"]
        app.config["AWS_S3_BUCKET"] = bucket_name
        app.config["AWS_S3_REGION"] = "test-region"

        uploader = S3Uploader()

        assert uploader.s3
        assert uploader.bucket == bucket_name

        fake_file = BytesIO("fakedfile".encode())
        with pytest.raises(ClientError) as ex:
            uploader.upload(fake_file, "fake_file.txt")

        assert ex.value.response["Error"]["Code"] == "AccessDenied"
        assert ex.value.response["ResponseMetadata"]["HTTPStatusCode"] == 403

    destroy_ctfd(app)
