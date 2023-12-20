import logging
import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    """
    Проверяет домашную страницу на предмет того, что возвращается код Success
    и подгружается корректный шаблон.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Find the Flag!" in response.data

# Test for logging
def test_logging_on_access(client, caplog):
    """
    Проверяет, записывается ли сообщение об успехе в логи
    """
    with caplog.at_level(logging.INFO):
        client.get('/')
        assert 'Homepage accessed' in caplog.text

