from docker.errors import DockerException, TLSParameterError, APIError, requests

from CTFd.utils import get_config

from .docker import get_docker_client
from .routers import Router, _routers


class WhaleChecks:
    @staticmethod
    def check_docker_api():
        try:
            client = get_docker_client()
        except TLSParameterError as e:
            return f'Docker TLS Parameters incorrect ({e})'
        except DockerException as e:
            return f'Docker API url incorrect ({e})'
        try:
            client.ping()
        except (APIError, requests.RequestException):
            return f'Unable to connect to Docker API, check your API connectivity'

        credentials = get_config("whale:docker_credentials")
        if credentials and credentials.count(':') == 1:
            try:
                client.login(*credentials.split(':'))
            except DockerException:
                return f'Unable to log into docker registry, check your credentials'
        swarm = client.info()['Swarm']
        if not swarm['ControlAvailable']:
            return f'Docker swarm not available. You should initialize a swarm first. ($ docker swarm init)'

    @staticmethod
    def check_frp_connection():
        router_conftype = get_config("whale:router_type", "frp")
        if router_conftype not in _routers:
            return "invalid router type: " + router_conftype
        ok, msg = _routers[router_conftype]().check_availability()
        if not ok:
            return msg

    @staticmethod
    def perform():
        errors = []
        for attr in dir(WhaleChecks):
            if attr.startswith('check_'):
                err = getattr(WhaleChecks, attr)()
                if err:
                    errors.append(err)
        return errors
