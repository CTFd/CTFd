import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Vulnerable App" in response.data

def test_ping_route_valid_ip(client):
    response = client.get('/ping?ip=127.0.0.1')
    assert response.status_code == 200
    assert b"PING 127.0.0.1 (127.0.0.1)" in response.data

def test_ping_route_invalid_ip(client):
    response = client.get('/ping?ip=invalid_ip')
    assert response.status_code == 200
    assert b"" in response.data

def test_404_error_handler(client):
    response = client.get('/nonexistentpage')
    assert response.status_code == 404
    assert b"404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again." in response.data
