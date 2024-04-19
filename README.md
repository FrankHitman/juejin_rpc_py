深入理解 RPC : 基于 Python 自建分布式高并发 RPC 服务
--
本小册代码运行环境为Mac和Linux，如果是windows用户，建议安装虚拟机

小册代码均基于Python2.7编写，第15章之前的所有代码只使用了内置library，没有任何第三方依赖项

第15章之后分布式RPC服务实践因为要用到zookeeper，所以需要安装kazoo库来和zk交互
```
pip install kazoo
```

安装zookeeper可以考虑使用docker进行快速安装
```
docker pull zookeeper
docker run -p 2181:2181 zookeeper
```

kazoo 最新版本(2.10.0)已经不支持 Python 2.7， 强制运行会报语法错误。
根据 [kazoo release notes](https://github.com/python-zk/kazoo/releases)，最后支持 Python 2.7 的是 kazoo 2.7 版本。
所以在安装 kazoo 时候需要指定版本号。
```
sudo pip install kazoo==2.7.0
```
第16章服务器端代码运行需要指定地址和端口，多端口以模拟多服务器节点
```
python server.py 127.0.0.1 8001
python server.py 127.0.0.1 8002
```


代码上如有任何问题，可以在官方的微信交流群里进行讨论
