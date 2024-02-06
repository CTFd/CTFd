from CTFd.models import Pages
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_previewing_pages_works():
    """Test that pages can be previewed properly"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "title": "title",
                "route": "route",
                "content": "content_testing",
                "nonce": sess.get("nonce"),
                "draft": True,
                "hidden": True,
                "auth_required": True,
            }

        r = client.post("/admin/pages/preview", data=data)
        assert r.status_code == 200
        resp = r.get_data(as_text=True)
        assert "content_testing" in resp

    destroy_ctfd(app)


def test_previewing_page_with_format_works():
    """Test that pages can be previewed properly"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "title": "title",
                "route": "route",
                "content": "# content_testing",
                "format": "markdown",
                "nonce": sess.get("nonce"),
                "draft": "y",
                "hidden": "y",
                "auth_required": "y",
            }

        r = client.post("/admin/pages/preview", data=data)
        assert r.status_code == 200
        resp = r.get_data(as_text=True)
        assert "<h1>content_testing</h1>" in resp

        with client.session_transaction() as sess:
            data = {
                "title": "title",
                "route": "route",
                "content": "<h1>content_testing</h1>",
                "format": "html",
                "nonce": sess.get("nonce"),
                "draft": "y",
                "hidden": "y",
                "auth_required": "y",
            }

        r = client.post("/admin/pages/preview", data=data)
        assert r.status_code == 200
        resp = r.get_data(as_text=True)
        assert "<h1>content_testing</h1>" in resp

    destroy_ctfd(app)


def test_pages_with_link_target():
    """Test that target=_blank links show in public interface"""
    ## TODO: Replace back to DEFAULT_THEME (aka core) in CTFd 4.0
    app = create_ctfd(ctf_theme="core-beta")
    with app.app_context():
        app.db.session.add(
            Pages(title="test", route="test", content="test", link_target="_blank")
        )
        app.db.session.commit()
        app.cache.clear()
        register_user(app)
        client = login_as_user(app)
        with client.session_transaction():
            r = client.get("/")
            html = r.get_data(as_text=True)
            assert "_blank" in html
    destroy_ctfd(app)
