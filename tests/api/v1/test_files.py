#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from io import BytesIO
import os


def test_api_files_get_non_admin():
    """Can a user get /api/v1/files if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/files', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_files_get_admin():
    """Can a user get /api/v1/files if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/files', json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_files_post_non_admin():
    """Can a user post /api/v1/files if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.post('/api/v1/files')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_files_post_admin():
    """Can a user post /api/v1/files if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name='admin') as client:
            with client.session_transaction() as sess:
                nonce = sess.get('nonce')
            r = client.post('/api/v1/files',
                            content_type='multipart/form-data',
                            data=dict(file=(BytesIO(b'test file content'), 'test.txt'),
                                      nonce=nonce))
            assert r.status_code == 200
            f = Files.query.filter_by(id=1).first()
            os.remove(
                os.path.join(app.config['UPLOAD_FOLDER'] + '/' + f.location)
            )
    destroy_ctfd(app)


def test_api_file_get_non_admin():
    """Can a user get /api/v1/files/<file_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_file(app.db, '0bf1a55a5cd327c07af15df260979668/bird.swf')
        assert Files.query.count() == 1
        with app.test_client() as client:
            r = client.get('/api/v1/files/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_file_get_admin():
    """Can a user get /api/v1/files/<file_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        f = gen_file(app.db, location='0bf1a55a5cd327c07af15df260979668/bird.swf', challenge_id=chal.id)
        assert Files.query.count() == 1
        assert ChallengeFiles.query.count() == 1
        assert f in chal.files
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/files/1', json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_file_delete_non_admin():
    """Can a user delete /api/v1/files/<file_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_file(app.db, '0bf1a55a5cd327c07af15df260979668/bird.swf')
        assert Files.query.count() == 1
        with app.test_client() as client:
            r = client.delete('/api/v1/files/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_file_delete_admin():
    """Can a user delete /api/v1/files/<file_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        f = gen_file(app.db, location='0bf1a55a5cd327c07af15df260979668/bird.swf', challenge_id=chal.id)
        assert Files.query.count() == 1
        assert ChallengeFiles.query.count() == 1
        assert f in chal.files
        with login_as_user(app, 'admin') as client:
            r = client.delete('/api/v1/files/1', json="")
            assert r.status_code == 200
            assert Files.query.count() == 0
            assert ChallengeFiles.query.count() == 0
            chal = Challenges.query.filter_by(id=1).first()
            assert f not in chal.files
    destroy_ctfd(app)
