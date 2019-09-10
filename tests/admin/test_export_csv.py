from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, gen_challenge


def test_export_csv_works():
    """Test that CSV exports work properly"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        client = login_as_user(app, name="admin", password="password")

        csv_data = client.get("/admin/export/csv?table=challenges").get_data(
            as_text=True
        )
        assert len(csv_data) > 0

    destroy_ctfd(app)
