# Chapter 11 Notes

## 多进程 PreForking 模型
采用 PreForking 模型可以对子进程的数量进行了限制。
PreForking 是通过预先产生多个子进程，共同对服务器套接字进行竞争性的 accept，
当一个连接到来时，每个子进程都有机会拿到这个连接，但是最终只会有一个进程能 accept 成功返回拿到连接。
子进程拿到连接后，进程内部可以继续使用单线程或者多线程同步的形式对连接进行处理。

```python
def prefork(n):
    for i in range(n):
        pid = os.fork()
        if pid < 0:  # fork error
            return
        if pid > 0:  # parent process
            continue
        if pid == 0:
            break  # child process
# ...
if __name__ == '__main__':
    # ...
    sock.listen(1)
    prefork(10)  # 好戏在这里，开启了 10 个子进程
    handlers = {
        "ping": ping
    }
    loop(sock, handlers)

```
Question: 
- 这里并没有像前一章中对父进程或者子进程的 connection，socket 进行关闭处理。为什么？

父进程 continue，子进程 break，说明是用父进程在循环中进行 fork，子进程跳出循环，避免子进程自己再创建子进程，子子孙孙无穷尽也。
每次子进程创建出来之后（拥有与父进程同样的资源）被放任去监听socket了。

- `prefork(10)`执行之后并没有对子进程进行控制或者管理，那么后期不用了，父进程还可以用waitpid进行收割么？

是否可以把pid存储在列表中，供父进程退出时候进行收割？
```python
import os
pid_list = []
def prefork(n):
    for i in range(n):
        pid = os.fork()
        if pid < 0:  # fork error
            return
        if pid > 0:  # parent process
            pid_list.append(pid)
            continue
        if pid == 0:
            break  # child process
```

```python
import os
# where parent process is going to exist
for pid in pid_list:
    os.waitpid(pid, 0)
```

- 父进程会监听 socket 并处理 connection 吗？

看着父进程与子进程应该都会处理，并没有特殊处理。从强制退出 prefork.py 进程的错误信息中也可以看出来，参见[prefork.py](prefork.py)

## Prefork plus multithread
如果并行的连接数超过了 prefork 进程的数量，那么后来的客户端请求将会阻塞，因为正在处理连接的子进程是没有机会去调用 accept 来获取新连接的。
为了不阻塞新的客户端，我们可以将子进程的单线程同步模型改成多线程同步模型即可。

Question:
- 如何在子进程里面写多线程？

参见 [prefork_multithread.py](prefork_multithread.py)，写的多线程处理既在子进程中又在父进程中，因为父进程也处理socket。


## accept 竞争
prefork 之后，父进程创建的服务套接字引用，每个子进程也会继承一份，它们共同指向了操作系统内核的套接字对象，共享了同一份连接监听队列。
子进程和父进程一样都可以对服务套接字进行 accept 调用，从共享的监听队列中摘取一个新连接进行处理。