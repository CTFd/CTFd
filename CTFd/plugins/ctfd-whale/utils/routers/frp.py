import json
import warnings

from flask import current_app
from requests import session, RequestException

from CTFd.models import db
from CTFd.utils import get_config, set_config, logging

from .base import BaseRouter
from ..cache import CacheProvider
from ..db import DBContainer
from ..exceptions import WhaleError, WhaleWarning
from ...models import WhaleContainer


class FrpRouter(BaseRouter):
    name = "frp"
    types = {
        'direct': 'tcp',
        'http': 'http',
    }

    class FrpRule:
        def __init__(self, name, config):
            self.name = name
            self.config = config

        @staticmethod
        def _toml_value(value):
            if isinstance(value, bool):
                return "true" if value else "false"
            if isinstance(value, (int, float)):
                return str(value)
            return json.dumps(str(value))

        def __str__(self):
            lines = [
                "[[proxies]]",
                f"name = {json.dumps(self.name)}",
            ]
            lines.extend(
                f"{key} = {self._toml_value(value)}"
                for key, value in self.config.items()
            )
            return "\n".join(lines)

    def __init__(self):
        super().__init__()
        self.ses = session()
        self.url = get_config("whale:frp_api_url").rstrip("/")
        self.common = ''
        try:
            CacheProvider(app=current_app).init_port_sets()
        except Exception:
            warnings.warn(
                "cache initialization failed",
                WhaleWarning
            )

    def reload(self, exclude=None):
        rules = []
        for container in DBContainer.get_all_alive_container():
            if container.uuid == exclude:
                continue
            name = f'{container.challenge.redirect_type}_{container.user_id}_{container.uuid}'
            config = {
                "type": self.types[container.challenge.redirect_type],
                "localIP": f"{container.user_id}-{container.uuid}",
                "localPort": int(container.challenge.redirect_port),
                "transport.useCompression": True,
            }
            if config["type"] == "http":
                config["subdomain"] = container.http_subdomain
            elif config["type"] == "tcp":
                config["remotePort"] = int(container.port)
            rules.append(self.FrpRule(name, config))

        try:
            if not self.common:
                common = get_config("whale:frp_config_template", "").strip()
                if common and "[common]" not in common:
                    self.common = common
                else:
                    remote = self.ses.get(f'{self.url}/api/config')
                    assert remote.status_code == 200
                    set_config("whale:frp_config_template", remote.text)
                    self.common = remote.text
            config = self.common + '\n' + '\n'.join(str(r) for r in rules)
            assert self.ses.put(
                f'{self.url}/api/config', config, timeout=5
            ).status_code == 200
            assert self.ses.get(
                f'{self.url}/api/reload', timeout=5
            ).status_code == 200
        except (RequestException, AssertionError) as e:
            raise WhaleError(
                '\nfrpc request failed\n' +
                (f'{e}\n' if str(e) else '') +
                'please check the frp related configs'
            ) from None

    def access(self, container: WhaleContainer):
        if container.challenge.redirect_type == 'direct':
            return f'nc {get_config("whale:frp_direct_ip_address", "127.0.0.1")} {container.port}'
        elif container.challenge.redirect_type == 'http':
            host = get_config("whale:frp_http_domain_suffix", "")
            port = get_config("whale:frp_http_port", "80")
            host += f':{port}' if port != '80' else ''
            return f'<a target="_blank" href="http://{container.http_subdomain}.{host}/">Link to the Challenge</a>'
        return ''

    def register(self, container: WhaleContainer):
        if container.challenge.redirect_type == 'direct':
            if not container.port:
                port = CacheProvider(app=current_app).get_available_port()
                if not port:
                    return False, 'No available ports. Please wait for a few minutes.'
                container.port = port
                db.session.commit()
        elif container.challenge.redirect_type == 'http':
            # config['subdomain'] = container.http_subdomain
            pass
        self.reload()
        return True, 'success'

    def unregister(self, container: WhaleContainer):
        if container.challenge.redirect_type == 'direct':
            try:
                redis_util = CacheProvider(app=current_app)
                redis_util.add_available_port(container.port)
            except Exception as e:
                logging.log(
                    'whale', 'Error deleting port from cache',
                    name=container.user.name,
                    challenge_id=container.challenge_id,
                )
                return False, 'Error deleting port from cache'
        self.reload(exclude=container.uuid)
        return True, 'success'

    def check_availability(self):
        try:
            resp = self.ses.get(f'{self.url}/api/status', timeout=2.0)
        except RequestException as e:
            return False, 'Unable to access frpc admin api'
        if resp.status_code == 401:
            return False, 'frpc admin api unauthorized'
        return True, 'Available'
