# Changelog

## 2020-03-18

- Allow non-dynamic flag.

## 2020-02-18

- Refine front for ctfd newer version.(@frankli0324)

## 2019-11-21

- Add network prefix & timeout setting.
- Refine port and network range search
- Refine frp request
- Refine lock timeout

## 2019-11-08

- Add Lan Domain

## 2019-11-04

- Change backend to Docker Swarm.
- Support depoly different os image to different os node.

You should init docker swarm, and add your node to it. And name them with following command:

```
docker node update --label-add name=windows-1 ****
docker node update --label-add name=linux-1 ****
```

Name of them should begin with windows- or linux-.

And put them in the setting panel.

Then if you want to deploy a instance to windows node, You should tag your name with prefix "windows", like "glzjin/super_sql:windows".

And please modify the container network driver to 'Overlay'!

## 2019-10-30

- Optimize for multi worker.
- Try to fix concurrency request problem.

Now You should set the redis with REDIS_HOST environment varible.

## 2019-09-26

- Add frp http port setting.

You should config it at the settings for http redirect.

## 2019-09-15

- Add Container Network Setting and DNS Setting.

Now You can setup a DNS Server in your Container Network.
- For single-instance network, Just connect your dns server to it and input the ip address in the seeting panel.
- For multi-instance network, You should rename the dns server to a name include "dns", than add it to auto connect instance. It will be used as a dns server.

## 2019-09-14

- Refine plugin path.

## 2019-09-13

- Refine removal.

## 2019-08-29

- Add CPU usage limit.
- Allow the multi-image challenge.

Upgrade:
1. Execute this SQL in ctfd database.

```
alter table dynamic_docker_challenge add column cpu_limit float default 0.5 after memory_limit;
```

2. Setting the containers you want to plugin to a single multi-image network. (In settings panel)

3. When you create a challenge you can set the docker image like this

```
{"socks": "serjs/go-socks5-proxy", "web": "blog_revenge_blog", "mysql": "blog_revenge_mysql", "oauth": "blog_revenge_oauth"}
```

The first one will be redirected the traffic.
