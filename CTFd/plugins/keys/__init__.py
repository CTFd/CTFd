from CTFd.plugins import register_plugin_assets_directory

import re
import string
import hmac
import requests
from CTFd.utils import get_lang, validate_url, get_team_token, get_authcode

PluginAssets = '/plugins/keys/assets/{0}/'.format(get_lang())

def JoinAssets(res):
    return PluginAssets + res
    
class BaseKey(object):
    id = None
    name = None
    templates = {}

    @staticmethod
    def compare(self, saved, provided):
        return True


class CTFdStaticKey(BaseKey):
    id = 0
    name = "static"
    templates = {  # Nunjucks templates used for key editing & viewing
        'create': JoinAssets('static/create-static-modal.njk'),
        'update': JoinAssets('static/edit-static-modal.njk'),
    }

    @staticmethod
    def compare(saved, provided):
        if len(saved) != len(provided):
            return False
        result = 0
        for x, y in zip(saved, provided):
            result |= ord(x) ^ ord(y)
        return result == 0


class CTFdRegexKey(BaseKey):
    id = 1
    name = "regex"
    templates = {  # Nunjucks templates used for key editing & viewing
        'create': JoinAssets('regex/create-regex-modal.njk'),
        'update': JoinAssets('regex/edit-regex-modal.njk'),
    }

    @staticmethod
    def compare(saved, provided):
        res = re.match(saved, provided, re.IGNORECASE)
        return res and res.group() == provided

class CTFdDynamicKey(BaseKey):
    id = 1
    name = "dynamic"
    templates = {  # Nunjucks templates used for key editing & viewing
        'create': JoinAssets('dynamic/create-dynamic-modal.njk'),
        'update': JoinAssets('dynamic/edit-dynamic-modal.njk'),
    }

    @staticmethod
    def compare(saved, provided):
        '''
        request a url with (key,token,auth) return http_status_code
        **USE [POST] method
        *key is flag provide by user (Don't be trusted)
        *token is user's Team-Token
        *auth is generate by system_sectet_key,use to identify we self
        **http_status_code=200 & Text='OKAY' will return true, other is false
        '''
        token = get_team_token()
        if token=='NULL':
            return False
        if (validate_url(saved)):
             try:
                r = requests.post(
                    saved,
                    data = {
                      "key": provided,
                      "token": token,
                      "auth":get_authcode()
                     },
                    timeout=3.0
                )
             except requests.RequestException as e:
                return False
             print r.status_code
             if r.status_code == 200 and r.text == 'OKAY':
                return True
             else:
                return False
        '''Not support yet'''
        return False
        
KEY_CLASSES = {
    'static': CTFdStaticKey,
    'regex': CTFdRegexKey,
    'dynamic': CTFdDynamicKey
    
}


def get_key_class(class_id):
    cls = KEY_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


def load(app):
    register_plugin_assets_directory(app, base_path=PluginAssets)
