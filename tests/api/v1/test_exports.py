from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    login_as_user,
    register_user,
)


def test_api_export_csv():
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        data = {
            "type": "csv",
            "args": {"table": "challenges"},
        }

        with login_as_user(app, name="admin", password="password") as client:
            r = client.post("/api/v1/exports/raw", json=data)
            assert r.status_code == 200
            assert r.headers["Content-Type"].startswith("text/csv")
            assert "chal_name" in r.get_data(as_text=True)

        # Test that regular users cannot access the endpoint
        register_user(app)
        with login_as_user(app) as client:
            response = client.post("/api/v1/exports/raw", json=data)
            assert response.status_code == 403
    destroy_ctfd(app)


def test_api_export():
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        data = {}

        with login_as_user(app, name="admin", password="password") as client:
            r = client.post("/api/v1/exports/raw", json=data)
            assert r.status_code == 200
            assert r.headers["Content-Type"].startswith("application/zip")

        # Test that regular users cannot access the endpoint
        register_user(app)
        with login_as_user(app) as client:
            response = client.post("/api/v1/exports/raw", json=data)
            assert response.status_code == 403
    destroy_ctfd(app)
