import traceback
from requests import session, RequestException, HTTPError

from CTFd.utils import get_config
from .base import BaseRouter
from ..db import DBContainer, WhaleContainer


class TrpRouter(BaseRouter):
    name = "trp"

    def __init__(self):
        super().__init__()
        self.ses = session()
        self.url = get_config('whale:trp_api_url', '').rstrip("/")
        self.common = ''
        for container in DBContainer.get_all_alive_container():
            self.register(container)

    @staticmethod
    def get_domain(container: WhaleContainer):
        domain = get_config('whale:trp_domain_suffix', '127.0.0.1.nip.io').lstrip('.')
        domain = f'{container.uuid}.{domain}'
        return domain

    def access(self, container: WhaleContainer):
        ch_type = container.challenge.redirect_type
        domain = self.get_domain(container)
        port = get_config('whale:trp_listening_port', 1443)
        if ch_type == 'direct':
            return f'from pwn import *<br>remote("{domain}", {port}, ssl=True).interactive()'
        elif ch_type == 'http':
            return f'https://{domain}' + (f':{port}' if port != 443 else '')
        else:
            return f'[ssl] {domain} {port}'

    def register(self, container: WhaleContainer):
        try:
            resp = self.ses.post(f'{self.url}/rule/{self.get_domain(container)}', json={
                'target': f'{container.user_id}-{container.uuid}:{container.challenge.redirect_port}',
                'source': None,
            })
            resp.raise_for_status()
            return True, 'success'
        except HTTPError as e:
            return False, e.response.text
        except RequestException as e:
            print(traceback.format_exc())
            return False, 'unable to access trp Api'

    def unregister(self, container: WhaleContainer):
        try:
            resp = self.ses.delete(f'{self.url}/rule/{self.get_domain(container)}')
            resp.raise_for_status()
            return True, 'success'
        except HTTPError as e:
            return False, e.response.text
        except RequestException as e:
            print(traceback.format_exc())
            return False, 'unable to access trp Api'

    def check_availability(self):
        try:
            resp = self.ses.get(f'{self.url}/rules').json()
        except RequestException as e:
            return False, 'Unable to access trp admin api'
        except Exception as e:
            return False, 'Unknown trp error'
        return True, 'Available'
