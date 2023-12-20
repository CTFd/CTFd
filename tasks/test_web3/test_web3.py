import pytest
import sqlite3
import os
from app import app as flask_app, create_database, DATABASE

@pytest.fixture
def app():
    test_db_path = "test_database.db"
    # создание тестовой БД 
    os.environ["DATABASE"] = "test_database.db"
    create_database()
    yield flask_app
    # сворачивание тестовой БД
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_successful_login(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'admin_password'})
    assert b"Flag" in response.data

def test_failed_login(client):
    response = client.post('/login', data={'username': 'wrong', 'password': 'wrong'})
    assert b"Login failed" in response.data

def test_database_creation():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    number_of_users = cursor.fetchone()[0]
    conn.close()
    assert number_of_users >= 2
