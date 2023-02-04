import logging
import traceback

import requests

from ..models.models import DockerConfig

logger = logging.getLogger(__name__)

def do_request(docker: DockerConfig, url: str, headers:dict=None, method:str='GET', data:dict=None)-> requests.Response:
    tls = docker.tls_enabled
    prefix = 'https' if tls else 'http'
    host = docker.hostname
    BASE_URL = f'{prefix}://{host}'
    if not headers:
        headers = {'Content-Type': "application/json"}
    try:
        if tls:
            if (method == 'GET'):
                r = requests.get(url=f"{BASE_URL}{url}", cert=(docker.client_cert, docker.client_key), verify=False, headers=headers)
            elif (method == 'POST'):
                r = requests.post(url=f"{BASE_URL}{url}", cert=(docker.client_cert, docker.client_key), verify=False, headers=headers,data=data)
            elif (method == 'DELETE'):
                r = requests.delete(url=f"{BASE_URL}{url}", cert=(docker.client_cert, docker.client_key), verify=False, headers=headers)
        else:
            if (method == 'GET'):
                r = requests.get(url=f"{BASE_URL}{url}", headers=headers)
            elif (method == 'POST'):
                r = requests.post(url=f"{BASE_URL}{url}", headers=headers,data=data)
            elif (method == 'DELETE'):
                r = requests.delete(url=f"{BASE_URL}{url}", headers=headers)
    except:
        print(traceback.print_exc())
        r = []
    return r

# For the Docker Config Page. Gets the Current Repositories available on the Docker Server.
def get_repositories(docker, tags=False, repos=False):
    r = do_request(docker, '/images/json?all=1')
    result = list()
    for i in r.json():
        if not i['RepoTags'] == None:
            if not i['RepoTags'][0].split(':')[0] == '<none>':
                if repos:
                    if not i['RepoTags'][0].split(':')[0] in repos:
                        continue
                if not tags:
                    result.append(i['RepoTags'][0].split(':')[0])
                else:
                    result.append(i['RepoTags'][0])
    return list(set(result))

def get_secrets(docker):
    r = do_request(docker, '/secrets')
    tmplist = list()
    for secret in r.json():
        tmpdict = {}
        tmpdict['ID'] = secret['ID']
        tmpdict['Name'] = secret['Spec']['Name']
        tmplist.append(tmpdict)
    return tmplist

def delete_secret(docker:DockerConfig, id: str):
    r = do_request(docker, f'/secrets/{id}', method='DELETE')
    return r.ok

def get_unavailable_ports(docker):
    r = do_request(docker, '/containers/json?all=1')
    result = list()
    for i in r.json():
        if not i['Ports'] == []:
            for p in i['Ports']:
                if p.get('PublicPort'):
                    result.append(p['PublicPort'])
    r = do_request(docker, '/services?all=1')
    for i in r.json():
        endpoint = i['Endpoint']['Spec']
        if not endpoint == {}:
            for p in endpoint['Ports']:
                if p.get('PublishedPort'):
                    result.append(p['PublishedPort'])
    return result


def get_required_ports(docker, image):
    r = do_request(docker, f'/images/{image}/json?all=1')
    result = r.json()['ContainerConfig']['ExposedPorts'].keys()
    return result