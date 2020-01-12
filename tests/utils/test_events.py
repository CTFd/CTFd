from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user
from CTFd.utils.events import ServerSentEvent, EventManager, RedisEventManager
from CTFd.config import TestingConfig
from mock import patch
from six.moves.queue import Queue
from collections import defaultdict
from redis.exceptions import ConnectionError
import json
import redis


def test_event_manager_installed():
    """Test that EventManager is installed on the Flask app"""
    app = create_ctfd()
    assert type(app.events_manager) == EventManager
    destroy_ctfd(app)


def test_event_manager_subscription():
    """Test that EventManager subscribing works"""
    with patch.object(Queue, "get") as fake_queue:
        saved_data = {
            "user_id": None,
            "title": "asdf",
            "content": "asdf",
            "team_id": None,
            "user": None,
            "team": None,
            "date": "2019-01-28T01:20:46.017649+00:00",
            "id": 10,
        }
        saved_event = {"type": "notification", "data": saved_data}

        fake_queue.return_value = saved_event
        event_manager = EventManager()
        for message in event_manager.subscribe():
            assert message.to_dict() == saved_event
            assert message.__str__().startswith("event:notification\ndata:")
            assert len(event_manager.clients) == 1
            break


def test_event_manager_publish():
    """Test that EventManager publishing to clients works"""
    saved_data = {
        "user_id": None,
        "title": "asdf",
        "content": "asdf",
        "team_id": None,
        "user": None,
        "team": None,
        "date": "2019-01-28T01:20:46.017649+00:00",
        "id": 10,
    }

    event_manager = EventManager()
    event_manager.clients.append(defaultdict(Queue))
    event_manager.publish(data=saved_data, type="notification", channel="ctf")

    event = event_manager.clients[0]["ctf"].get()
    event = ServerSentEvent(**event)
    assert event.data == saved_data


def test_event_endpoint_is_event_stream():
    """Test that the /events endpoint is text/event-stream"""
    app = create_ctfd()
    with patch.object(Queue, "get") as fake_queue:
        saved_data = {
            "user_id": None,
            "title": "asdf",
            "content": "asdf",
            "team_id": None,
            "user": None,
            "team": None,
            "date": "2019-01-28T01:20:46.017649+00:00",
            "id": 10,
        }
        saved_event = {"type": "notification", "data": saved_data}

        fake_queue.return_value = saved_event
        with app.app_context():
            register_user(app)
            with login_as_user(app) as client:
                r = client.get("/events")
                assert "text/event-stream" in r.headers["Content-Type"]
    destroy_ctfd(app)


def test_redis_event_manager_installed():
    """Test that RedisEventManager is installed on the Flask app"""

    class RedisConfig(TestingConfig):
        REDIS_URL = "redis://localhost:6379/1"
        CACHE_REDIS_URL = "redis://localhost:6379/1"
        CACHE_TYPE = "redis"

    try:
        app = create_ctfd(config=RedisConfig)
    except ConnectionError:
        print("Failed to connect to redis. Skipping test.")
    else:
        with app.app_context():
            assert isinstance(app.events_manager, RedisEventManager)
        destroy_ctfd(app)


def test_redis_event_manager_subscription():
    """Test that RedisEventManager subscribing works."""

    class RedisConfig(TestingConfig):
        REDIS_URL = "redis://localhost:6379/2"
        CACHE_REDIS_URL = "redis://localhost:6379/2"
        CACHE_TYPE = "redis"

    try:
        app = create_ctfd(config=RedisConfig)
    except ConnectionError:
        print("Failed to connect to redis. Skipping test.")
    else:
        with app.app_context():
            saved_data = {
                "data": {
                    "content": "asdf",
                    "date": "2019-01-28T05:02:19.830906+00:00",
                    "id": 13,
                    "team": None,
                    "team_id": None,
                    "title": "asdf",
                    "user": None,
                    "user_id": None,
                },
                "type": "notification",
            }

            saved_event = {
                "pattern": None,
                "type": "message",
                "channel": "ctf",
                "data": json.dumps(saved_data),
            }
            with patch.object(redis.client.PubSub, "listen") as fake_pubsub_listen:
                fake_pubsub_listen.return_value = [saved_event]
                event_manager = RedisEventManager()
                for message in event_manager.subscribe():
                    assert isinstance(message, ServerSentEvent)
                    assert message.to_dict() == saved_data
                    assert message.__str__().startswith("event:notification\ndata:")
                    break
        destroy_ctfd(app)


def test_redis_event_manager_publish():
    """Test that RedisEventManager publishing to clients works."""

    class RedisConfig(TestingConfig):
        REDIS_URL = "redis://localhost:6379/3"
        CACHE_REDIS_URL = "redis://localhost:6379/3"
        CACHE_TYPE = "redis"

    try:
        app = create_ctfd(config=RedisConfig)
    except ConnectionError:
        print("Failed to connect to redis. Skipping test.")
    else:
        with app.app_context():
            saved_data = {
                "user_id": None,
                "title": "asdf",
                "content": "asdf",
                "team_id": None,
                "user": None,
                "team": None,
                "date": "2019-01-28T01:20:46.017649+00:00",
                "id": 10,
            }

            event_manager = RedisEventManager()
            event_manager.publish(data=saved_data, type="notification", channel="ctf")
        destroy_ctfd(app)
