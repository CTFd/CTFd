# Installation & Usage Guide

## TLDR

If you never deployed a CTFd instance before:

```sh
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
docker swarm init
docker node update --label-add='name=linux-1' $(docker node ls -q)

git clone https://github.com/CTFd/CTFd --depth=1
git clone https://github.com/frankli0324/ctfd-whale CTFd/CTFd/plugins/ctfd-whale --depth=1
curl -fsSL https://cdn.jsdelivr.net/gh/frankli0324/ctfd-whale/docker-compose.example.yml -o CTFd/docker-compose.yml

# make sure you have pip3 installed on your rig
pip3 install docker-compose
docker-compose -f CTFd/docker-compose.yml up -d
# wait till the containers are ready
docker-compose -f CTFd/docker-compose.yml exec ctfd python manage.py set_config whale:auto_connect_network
```

The commands above tries to install `docker-ce`，`python3-pip` and `docker-compose`. Make sure the following requirements are satisfied before you execute them:

* have `curl`, `git`, `python3` and `pip` installed
* GitHub is reachable
* Docker Registry is reachable

## Installation

### Start from scratch

First of all, you should initialize a docker swarm and label the nodes

names of nodes running linux/windows should begin with `linux/windows-*`

```bash
docker swarm init
docker node update --label-add "name=linux-1" $(docker node ls -q)
```

Taken advantage of the orchestration ability of `docker swarm`, `ctfd-whale` is able to distribute challenge containers to different nodes(machines). Each time a user request for a challenge container, `ctfd-whale` will randomly pick a suitable node for running the container.

After initializing a swarm, make sure that CTFd runs as expected on your PC/server

Note that the included compose file in CTFd 2.5.0+ starts an nginx container by default, which takes the http/80 port. make sure there's no conflicts.

```bash
git clone https://github.com/CTFd/CTFd --depth=1
cd CTFd  # the cwd will not change throughout this guide from this line on
```

Change the first line of `docker-compose.yml` to support `attachable` property

`version '2'` -> `version '3'`

```bash
docker-compose up -d
```

take a look at <http://localhost>(or port 8000) and setup CTFd

### Configure frps

frps could be started by docker-compose along with CTFd

define a network for communication between frpc and frps, and create a frps service block

```yml
services:
    ...
    frps:
        image: glzjin/frp
        restart: always
        volumes:
            - ./conf/frp:/conf
        entrypoint:
            - /usr/local/bin/frps
            - -c
            - /conf/frps.ini
        ports:
            - 10000-10100:10000-10100  # for "direct" challenges
            - 8001:8001  # for "http" challenges
        networks:
            default:  # frps ports should be mapped to host
            frp_connect:

networks:
    ...
    frp_connect:
        driver: overlay
        internal: true
        ipam:
            config:
                - subnet: 172.1.0.0/16
```

Create a folder in `conf/` called `frp`

```bash
mkdir ./conf/frp
```

then create a configuration file for frps `./conf/frp/frps.ini`, and fill it with:

```ini
[common]
# following ports must not overlap with "direct" port range defined in the compose file
bind_port = 7987  # port for frpc to connect to
vhost_http_port = 8001  # port for mapping http challenges
token = your_token
subdomain_host = node3.buuoj.cn
# hostname that's mapped to frps by some reverse proxy (or IS frps itself)
```

### Configure frpc

Likewise, create a network and a service for frpc

the network allows challenges to be accessed by frpc

```yml
services:
    ...
    frpc:
        image: glzjin/frp:latest
        restart: always
        volumes:
          - ./conf/frp:/conf/
        entrypoint:
          - /usr/local/bin/frpc
          - -c
          - /conf/frpc.ini
        depends_on:
          - frps #need frps to run first
        networks:
            frp_containers:
            frp_connect:
                ipv4_address: 172.1.0.3

networks:
    ...
    frp_containers:  # challenge containers are attached to this network
        driver: overlay
        internal: true
        # if challenge containers are allowed to access the internet, remove this line
        attachable: true
        ipam:
            config:
                - subnet: 172.2.0.0/16
```

Likewise, create an frpc config file `./conf/frp/frpc.ini`

```ini
[common]
token = your_token
server_addr = frps
server_port = 7897  # == frps.bind_port
admin_addr = 172.1.0.3  # refer to "Security"
admin_port = 7400
```

### Verify frp configurations

update compose stack with `docker-compose up -d`

by executing `docker-compose logs frpc`, you should see that frpc produced following logs:

```log
[service.go:224] login to server success, get run id [******], server udp port [******]
[service.go:109] admin server listen on ******
```

by seeing this, you can confirm that frpc/frps is set up correctly.

Note: folder layout in this guide:

```
CTFd/
    conf/
        nginx/  # included in CTFd 2.5.0+
        frp/
            frpc.ini
            frps.ini
    serve.py <- this is just an anchor
```

### Configure CTFd

After finishing everything above:

* map docker socket into CTFd container
* Attach CTFd container to frp_connect

```yml
services:
    ctfd:
        ...
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
        depends_on:
            - frpc #need frpc to run ahead
        networks:
            ...
            frp_connect:
```

and then clone Whale into CTFd plugins directory (yes, finally)

```bash
git clone https://github.com/frankli0324/CTFd-Whale CTFd/plugins/ctfd-whale --depth=1
docker-compose build # for pip to find requirements.txt
docker-compose up -d
```

go to the Whale Configuration page (`/plugins/ctfd-whale/admin/settings`)

#### Docker related configs

`Auto Connect Network`, if you strictly followed the guide, should be `ctfd_frp_containers`

If you're not sure about that, this command lists all networks in the current stack

```bash
docker network ls -f "label=com.docker.compose.project=ctfd" --format "{{.Name}}"
```

#### frp related configs

* `HTTP Domain Suffix` should be consistent with `subdomain_host` in frps
* `HTTP Port` with `vhost_http_port` in frps
* `Direct IP Address` should be a hostname/ip address that can be used to access frps
* `Direct Minimum Port` and `Direct Maximum Port`, you know what to do
* as long as `API URL` is filled in correctly, Whale will read the config of the connected frpc into `Frpc config template`
* setting `Frpc config template` will override contents in `frpc.ini`

Whale should be kinda usable at this moment.

### Configure nginx

If you are using CTFd 2.5.0+, you can utilize the included nginx.

remove the port mapping rule for frps vhost http port(8001) in the compose file

If you wnat to go deeper:

* add nginx to `default` and `internal` network
* remove CTFd from `default` and remove the mapped 8000 port

add following server block to `./conf/nginx/nginx.conf`:

```conf
server {
  listen 80;
  server_name *.node3.buuoj.cn;
  location / {
    proxy_pass http://frps:8001;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Host $server_name;
  }
}
```

## Challenge Deployment

### Standalone Containers

Take a look at <https://github.com/CTFTraining>

In one word, a `FLAG` variable will be passed into the container when it's started. You should write your own startup script (usually with bash and sed) to:

* replace your flag with the generated flag
* remove or override the `FLAG` variable

PLEASE create challenge images with care.

### Grouped Containers

"name" the challenge image with a json object, for example:

```json
{
    "hostname": "image",
}
```

Whale will keep the order of the keys in the json object, and take the first image as the "main container" of a challenge. The "main container" will be mapped to frp with same rules from standalone containers

see how grouped containers are created in the [code](utils/docker.py#L58)

## Security

* Please do not allow untrusted people to access the admin account. Theoretically there's an SSTI vulnerability in the config page.
* Do not set bind_addr of the frpc to `0.0.0.0` if you are following this guide. This may enable contestants to override frpc configurations.
* If you are annoyed by the complicated configuration, and you just want to set bind_addr = 0.0.0.0, remember to enable Basic Auth included in frpc, and set API URL accordingly, for example, `http://username:password@frpc:7400`

## Advanced Deployment

To separate the target server (for lunching instance) and CTFd web server with TLS secured docker API, please refer to [this document](advanced.md)