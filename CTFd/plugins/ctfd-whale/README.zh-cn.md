# CTFd-Whale

能够支持题目容器化部署的CTFd插件

## 功能

- 利用`frp`与`docker swarm`做到多容器部署
- web题目支持利用frp的subdomain实现每个用户单独的域名访问
- 参赛选手一键启动题目环境，支持容器续期
- 自动生成随机flag，并通过环境变量传入容器
- 管理员可以在后台查看启动的容器
- 支持自定义flag生成方式与web题目子域名生成方式

## 使用方式

请参考[安装指南](docs/install.zh-cn.md)

请注意whale假设`CACHE_TYPE=redis`。配置使用别的缓存方式可能会导致异常行为。

## Demo

[BUUCTF](https://buuoj.cn)

## 第三方使用说明

- [CTFd-Whale 推荐部署实践](https://www.zhaoj.in/read-6333.html)
- [手把手教你如何建立一个支持ctf动态独立靶机的靶场（ctfd+ctfd-whale)](https://blog.csdn.net/fjh1997/article/details/100850756)

## 使用案例

![](https://user-images.githubusercontent.com/20221896/105939593-7cca6f80-6094-11eb-92de-8a04554dc019.png)

![image](https://user-images.githubusercontent.com/20221896/105940182-a637cb00-6095-11eb-9525-8291986520c1.png)

![](https://user-images.githubusercontent.com/20221896/105939965-2e69a080-6095-11eb-9b31-7777a0cc41b9.png)

![](https://user-images.githubusercontent.com/20221896/105940026-50632300-6095-11eb-8512-6f19dd12c776.png)

## 友情链接

- [CTFd-Owl](https://github.com/D0g3-Lab/H1ve/tree/master/CTFd/plugins/ctfd-owl) (支持部署compose)
