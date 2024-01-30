#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
from io import BytesIO

from CTFd.models import ChallengeFiles, Challenges, Files
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_file,
    login_as_user,
)


def test_api_files_get_non_admin():
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_file(
            app.db,
            location="0bf1a55a5cd327c07af15df260979668/bird.swf",
            challenge_id=chal.id,
        )

        with app.test_client() as client:
            # test_api_files_get_non_admin
            """Can a user get /api/v1/files if not admin"""
            r = client.get("/api/v1/files", json="")
            assert r.status_code == 403

            # test_api_files_post_non_admin
            """Can a user post /api/v1/files if not admin"""
            r = client.post("/api/v1/files")
            assert r.status_code == 403

            # test_api_file_get_non_admin
            """Can a user get /api/v1/files/<file_id> if not admin"""
            r = client.get("/api/v1/files/1", json="")
            assert r.status_code == 403

            # test_api_file_delete_non_admin
            """Can a user delete /api/v1/files/<file_id> if not admin"""
            r = client.delete("/api/v1/files/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_files_get_admin():
    """Can a user get /api/v1/files if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/files", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_files_post_admin():
    """Can a user post /api/v1/files if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            with client.session_transaction() as sess:
                nonce = sess.get("nonce")
            r = client.post(
                "/api/v1/files",
                content_type="multipart/form-data",
                data={
                    "file": (BytesIO(b"test file content"), "test.txt"),
                    "nonce": nonce,
                },
            )
            assert r.status_code == 200
            f = Files.query.filter_by(id=1).first()
            assert f.sha1sum == "9032bbc224ed8b39183cb93b9a7447727ce67f9d"
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"] + "/" + f.location))
    destroy_ctfd(app)


def test_api_file_get_admin():
    """Can a user get /api/v1/files/<file_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        f = gen_file(
            app.db,
            location="0bf1a55a5cd327c07af15df260979668/bird.swf",
            challenge_id=chal.id,
        )
        assert Files.query.count() == 1
        assert ChallengeFiles.query.count() == 1
        assert f in chal.files
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/files/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_file_delete_admin():
    """Can a user delete /api/v1/files/<file_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        path = os.path.join(
            app.config["UPLOAD_FOLDER"], "0bf1a55a5cd327c07af15df260979668", "bird.swf"
        )
        try:
            # Create a fake file
            os.makedirs(os.path.dirname(path))
            open(path, "a").close()
            f = gen_file(
                app.db,
                location="0bf1a55a5cd327c07af15df260979668/bird.swf",
                challenge_id=chal.id,
            )
            assert Files.query.count() == 1
            assert ChallengeFiles.query.count() == 1
            assert f in chal.files

            # Make sure the file was created
            assert os.path.exists(path)

            with login_as_user(app, "admin") as client:
                r = client.delete("/api/v1/files/1", json="")
                assert r.status_code == 200
                assert Files.query.count() == 0
                assert ChallengeFiles.query.count() == 0
                chal = Challenges.query.filter_by(id=1).first()
                assert f not in chal.files

                # Make sure the API call deleted the file
                assert os.path.exists(path) is False
        finally:
            # Always make sure the file is deleted
            shutil.rmtree(os.path.dirname(path), ignore_errors=True)

    destroy_ctfd(app)


def test_api_file_custom_location():
    """
    Test file uploading with custom location
    """
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            with client.session_transaction() as sess:
                nonce = sess.get("nonce")
            r = client.post(
                "/api/v1/files",
                content_type="multipart/form-data",
                data={
                    "file": (BytesIO(b"test file content"), "test.txt"),
                    "location": "testing/asdf.txt",
                    "nonce": nonce,
                },
            )
            assert r.status_code == 200
            f = Files.query.filter_by(id=1).first()
            assert f.sha1sum == "9032bbc224ed8b39183cb93b9a7447727ce67f9d"
            assert f.location == "testing/asdf.txt"
            r = client.get("/files/" + f.location)
            assert r.get_data(as_text=True) == "test file content"

            r = client.get("/api/v1/files/1")
            response = r.get_json()
            assert (
                response["data"]["sha1sum"]
                == "9032bbc224ed8b39183cb93b9a7447727ce67f9d"
            )
            assert response["data"]["location"] == "testing/asdf.txt"

            # Test deletion
            r = client.delete("/api/v1/files/1", json="")
            assert r.status_code == 200
            assert Files.query.count() == 0

            target = pathlib.Path(app.config["UPLOAD_FOLDER"]) / f.location
            assert target.exists() is False

            # Test invalid locations
            invalid_paths = [
                "testing/prefix/asdf.txt",
                "/testing/asdf.txt",
                "asdf.txt",
            ]
            for path in invalid_paths:
                r = client.post(
                    "/api/v1/files",
                    content_type="multipart/form-data",
                    data={
                        "file": (BytesIO(b"test file content"), "test.txt"),
                        "location": path,
                        "nonce": nonce,
                    },
                )
                assert r.status_code == 400
    destroy_ctfd(app)


def test_api_file_overwrite_by_location():
    """
    Test file overwriting with a specific location
    """
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            with client.session_transaction() as sess:
                nonce = sess.get("nonce")
            r = client.post(
                "/api/v1/files",
                content_type="multipart/form-data",
                data={
                    "file": (BytesIO(b"test file content"), "test.txt"),
                    "location": "testing/asdf.txt",
                    "nonce": nonce,
                },
            )
            assert r.status_code == 200
            f = Files.query.filter_by(id=1).first()
            r = client.get("/files/" + f.location)
            assert r.get_data(as_text=True) == "test file content"

            r = client.post(
                "/api/v1/files",
                content_type="multipart/form-data",
                data={
                    "file": (BytesIO(b"testing new uploaded file content"), "test.txt"),
                    "location": "testing/asdf.txt",
                    "nonce": nonce,
                },
            )
            assert r.status_code == 200
            f = Files.query.filter_by(id=1).first()
            r = client.get("/files/" + f.location)
            assert f.sha1sum == "0ee7eb85ac0b8d8ae03f3080589157cde553b13f"
            assert r.get_data(as_text=True) == "testing new uploaded file content"
    destroy_ctfd(app)
