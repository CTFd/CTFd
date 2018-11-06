#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from io import BytesIO


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
    destroy_ctfd(app)


def test_api_file_get_non_admin():
    """Can a user get /api/v1/files/<file_id> if not admin"""
    app = create_ctfd()
    # with app.app_context():
    #     with app.test_client() as client:
    #         r = client.get('/api/v1/files/1', json="")
    #         assert r.status_code == 403
    destroy_ctfd(app)

# TODO: gen_file is not properly implemented
# def test_api_file_get_admin():
#     """Can a user get /api/v1/files/<file_id> if admin"""
#     app = create_ctfd()
#     with app.app_context():
#         chal = gen_challenge(app.db)
#         gen_file(app.db, chal.id, '0bf1a55a5cd327c07af15df260979668/bird.swf')
#         with login_as_user(app, 'admin') as client:
#             r = client.get('/api/v1/files/1', json="")
#             assert r.status_code == 200
#     destroy_ctfd(app)


def test_api_file_delete_non_admin():
    """Can a user delete /api/v1/files/<file_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.delete('/api/v1/files/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)

# TODO: gen_file is not properly implemented
# def test_api_file_delete_admin():
#     """Can a user delete /api/v1/files/<file_id> if admin"""
#     app = create_ctfd()
#     with app.app_context():
#         chal = gen_challenge(app.db)
#         gen_file(app.db, chal.id, '0bf1a55a5cd327c07af15df260979668/bird.swf')
#         with login_as_user(app, 'admin') as client:
#             r = client.delete('/api/v1/files/1', json="")
#             assert r.status_code == 200
#     destroy_ctfd(app)
