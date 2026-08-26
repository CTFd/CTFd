import ipaddress
import warnings
from CTFd.cache import cache
from CTFd.utils import get_config
from flask_redis import FlaskRedis
from redis.exceptions import LockError

from .db import DBContainer


class CacheProvider:
    def __init__(self, app, *args, **kwargs):
        if app.config['CACHE_TYPE'] == 'redis':
            self.provider = RedisCacheProvider(app, *args, **kwargs)
        elif app.config['CACHE_TYPE'] in ['filesystem', 'simple']:
            if not hasattr(CacheProvider, 'cache'):
                CacheProvider.cache = {}
            self.provider = FilesystemCacheProvider(app, *args, **kwargs)
            self.init_port_sets()

    def init_port_sets(self):
        self.clear()

        containers = DBContainer.get_all_container()
        used_port_list = []
        for container in containers:
            if container.port != 0:
                used_port_list.append(container.port)
        for port in range(int(get_config("whale:frp_direct_port_minimum", 28000)),
                          int(get_config("whale:frp_direct_port_maximum", 29000)) + 1):
            if port not in used_port_list:
                self.add_available_port(port)

        from .docker import get_docker_client
        client = get_docker_client()

        docker_subnet = get_config("whale:docker_subnet", "174.1.0.0/16")
        docker_subnet_new_prefix = int(
            get_config("whale:docker_subnet_new_prefix", "24"))

        exist_networks = []
        available_networks = []

        for network in client.networks.list(filters={'label': 'prefix'}):
            exist_networks.append(str(network.attrs['Labels']['prefix']))

        for network in list(ipaddress.ip_network(docker_subnet).subnets(new_prefix=docker_subnet_new_prefix)):
            if str(network) not in exist_networks:
                available_networks.append(str(network))

        self.add_available_network_range(*set(available_networks))

    def __getattr__(self, name):
        return self.provider.__getattribute__(name)


class FilesystemCacheProvider:
    def __init__(self, app, *args, **kwargs):
        warnings.warn(
            '\n[CTFd Whale] Warning: looks like you are using filesystem cache. '
            '\nThis is for TESTING purposes only, DO NOT USE on production sites.',
            RuntimeWarning
        )
        self.key = 'ctfd_whale_lock-' + str(kwargs.get('user_id', 0))
        self.global_port_key = "ctfd_whale-port-set"
        self.global_network_key = "ctfd_whale-network-set"

    def clear(self):
        cache.set(self.global_port_key, set())
        cache.set(self.global_network_key, set())

    def add_available_network_range(self, *ranges):
        s = cache.get(self.global_network_key)
        s.update(ranges)
        cache.set(self.global_network_key, s)

    def get_available_network_range(self):
        try:
            s = cache.get(self.global_network_key)
            r = s.pop()
            cache.set(self.global_network_key, s)
            return r
        except KeyError:
            return None

    def add_available_port(self, port):
        s = cache.get(self.global_port_key)
        s.add(port)
        cache.set(self.global_port_key, s)

    def get_available_port(self):
        try:
            s = cache.get(self.global_port_key)
            r = s.pop()
            cache.set(self.global_port_key, s)
            return r
        except KeyError:
            return None

    def acquire_lock(self):
        # for testing purposes only, so no need to set this limit
        return True

    def release_lock(self):
        return True

    def acquire_global_lock(self):
        return True

    def release_global_lock(self):
        return True


class RedisCacheProvider(FlaskRedis):
    _GLOBAL_CONTAINER_LOCK = 'ctfd_whale_global_container_lock'

    def __init__(self, app, *args, **kwargs):
        super().__init__(app)
        self.key = 'ctfd_whale_lock-' + str(kwargs.get('user_id', 0))
        self.current_lock = None
        self._global_lock = None
        self.global_port_key = "ctfd_whale-port-set"
        self.global_network_key = "ctfd_whale-network-set"

    def clear(self):
        self.delete(self.global_port_key)
        self.delete(self.global_network_key)

    def add_available_network_range(self, *ranges):
        self.sadd(self.global_network_key, *ranges)

    def get_available_network_range(self):
        return self.spop(self.global_network_key).decode()

    def add_available_port(self, port):
        self.sadd(self.global_port_key, str(port))

    def get_available_port(self):
        return int(self.spop(self.global_port_key))

    def acquire_lock(self):
        lock = self.lock(name=self.key, timeout=10)

        if not lock.acquire(blocking=True, blocking_timeout=2.0):
            return False

        self.current_lock = lock
        return True

    def release_lock(self):
        if self.current_lock is None:
            return False

        try:
            self.current_lock.release()

            return True
        except LockError:
            return False

    def acquire_global_lock(self):
        lock = self.lock(name=self._GLOBAL_CONTAINER_LOCK, timeout=10)
        if not lock.acquire(blocking=True, blocking_timeout=5.0):
            return False
        self._global_lock = lock
        return True

    def release_global_lock(self):
        if self._global_lock is None:
            return False
        try:
            self._global_lock.release()
            return True
        except LockError:
            return False
