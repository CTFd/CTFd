import json
from collections import defaultdict
from queue import Queue

from gevent import Timeout

from CTFd.cache import cache
from CTFd.utils import string_types


class ServerSentEvent(object):
    def __init__(self, data, type=None, id=None):
        self.data = data
        self.type = type
        self.id = id

    def __str__(self):
        if isinstance(self.data, string_types):
            data = self.data
        else:
            data = json.dumps(self.data)
        lines = ["data:{value}".format(value=line) for line in data.splitlines()]
        if self.type:
            lines.insert(0, "event:{value}".format(value=self.type))
        if self.id:
            lines.append("id:{value}".format(value=self.id))
        return "\n".join(lines) + "\n\n"

    def to_dict(self):
        d = {"data": self.data}
        if self.type:
            d["type"] = self.type
        if self.id:
            d["id"] = self.id
        return d


class EventManager(object):
    def __init__(self):
        self.clients = []

    def publish(self, data, type=None, channel="ctf"):
        event = ServerSentEvent(data, type=type)
        message = event.to_dict()
        for client in self.clients:
            client[channel].put(message)
        return len(self.clients)

    def subscribe(self, channel="ctf"):
        q = defaultdict(Queue)
        self.clients.append(q)
        while True:
            try:
                # Immediately yield a ping event to force Response headers to be set
                # or else some reverse proxies will incorrectly buffer SSE
                yield ServerSentEvent(data="", type="ping")

                with Timeout(10):
                    message = q[channel].get()
                    yield ServerSentEvent(**message)
            except Timeout:
                yield ServerSentEvent(data="", type="ping")
            except Exception:
                raise


class RedisEventManager(EventManager):
    def __init__(self):
        super(EventManager, self).__init__()
        self.client = cache.cache._write_client

    def publish(self, data, type=None, channel="ctf"):
        event = ServerSentEvent(data, type=type)
        message = json.dumps(event.to_dict())
        return self.client.publish(message=message, channel=channel)

    def subscribe(self, channel="ctf"):
        while True:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            try:
                # Immediately yield a ping event to force Response headers to be set
                # or else some reverse proxies will incorrectly buffer SSE
                yield ServerSentEvent(data="", type="ping")

                with Timeout(10) as timeout:
                    for message in pubsub.listen():
                        if message["type"] == "message":
                            event = json.loads(message["data"])
                            yield ServerSentEvent(**event)
                            timeout.cancel()
                            timeout.start()
            except Timeout:
                yield ServerSentEvent(data="", type="ping")
            except Exception:
                raise
