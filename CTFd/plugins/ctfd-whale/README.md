# CTFd-Whale

## [中文README](README.zh-cn.md)

A plugin that empowers CTFd to bring up separate environments for each user

## Features

- Deploys containers with `frp` and `docker swarm`
- Supports subdomain access by utilizing `frp`
- Contestants can start/renew/destroy their environments with a single click
- flags and subdomains are generated automatically with configurable rules
- Administrators can get a full list of running containers, with full control over them.

## Installation & Usage

refer to [installation guide](docs/install.md)

Please note that whale assumes `CACHE_TYPE=redis`. Using other cache types may cause unexpected issues.

## Demo

[BUUCTF](https://buuoj.cn)

## Third-party Introductions (zh-CN)

- [CTFd-Whale 推荐部署实践](https://www.zhaoj.in/read-6333.html)
- [手把手教你如何建立一个支持ctf动态独立靶机的靶场（ctfd+ctfd-whale)](https://blog.csdn.net/fjh1997/article/details/100850756)

## Screenshots

![](https://user-images.githubusercontent.com/20221896/105939593-7cca6f80-6094-11eb-92de-8a04554dc019.png)

![image](https://user-images.githubusercontent.com/20221896/105940182-a637cb00-6095-11eb-9525-8291986520c1.png)

![](https://user-images.githubusercontent.com/20221896/105939965-2e69a080-6095-11eb-9b31-7777a0cc41b9.png)

![](https://user-images.githubusercontent.com/20221896/105940026-50632300-6095-11eb-8512-6f19dd12c776.png)

## Twin Project

- [CTFd-Owl](https://github.com/D0g3-Lab/H1ve/tree/master/CTFd/plugins/ctfd-owl) (支持部署compose)
