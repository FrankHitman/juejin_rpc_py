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

代码上如有任何问题，可以在官方的微信交流群里进行讨论

## Preparation for environment
From chapter 8 to chapter 13, it is required Python 2.7 environment.

Install Python2.7.18 on MacOS 13
```commandline
brew install pyenv
pyenv install 2.7.18
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile

cd path/to/this/folder
pyenv local 2.7.18
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
```

From chapter 14, it is required to use Python 3.5+

Install Python 3.12.2 on MacOS 13
```
deactivate
pyenv install 3.12.2
cd path/to/this/folder
pyenv local 3.12.2
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
```

Because distutils package is removed in python version 3.12,
roll back to Python 3.11.8

refer to 
- [stackoverflow](https://stackoverflow.com/questions/69919970/no-module-named-distutils-but-distutils-installed)
- [Python organization](https://docs.python.org/3.12/whatsnew/3.12.html)



