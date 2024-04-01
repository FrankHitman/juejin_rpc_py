# Chapter 10 Notes

## os.fork()

fork 调用将生成一个子进程，所以这个函数会在父子进程同时返回。

- 在父进程的返回结果是一个整数值，这个值是子进程的进程号，父进程可以使用该进程号来控制子进程的运行。
- fork 在子进程的返回结果是零。如果 fork 返回值小于零，一般意味着操作系统资源不足，无法创建进程。

我们可以通过 fork 调用的返回值来区分当前的进程是父进程还是子进程。

详细执行代码情况，参见 [play_fork.py](play_fork.py) 文件

子进程创建后，父进程拥有的很多操作系统资源，子进程也会持有。
比如套接字和文件描述符，它们本质上都是对操作系统内核对象的一个引用。
如果子进程不需要某些引用，一定要即时关闭它，避免操作系统资源得不到释放导致资源泄露。

MacOS 中 `os.fork()` 方法在 posix.py 文件中

```python
def fork():  # real signature unknown; restored from __doc__
    """
    fork() -> pid
    
    Fork a child process.
    Return 0 to child process and PID of child to parent process.
    """
    pass


# options:	It is an integer value representing what type of operations will be carried out 
# on the process after it is completed. The default value is 0.
def waitpid(pid, options):  # real signature unknown; restored from __doc__
    """
    waitpid(pid, options) -> (pid, status)
    
    Wait for completion of a given child process.
    """
    pass

def getpid(): # real signature unknown; restored from __doc__
    """
    getpid() -> pid
    
    Return the current process id
    """
    pass

```

## 多进程同步模型

### waitpid
子进程创建容易，销毁难。
当子进程退出后，父进程需要使用 waitpid 系统调用收割子进程，否则子进程将成为僵尸进程，
僵尸进程会持续占据操作系统的资源直到父进程退出后被 init 进程接管收割后才会消失释放资源。

关于 `os.waitpid()` 的使用参见 [play_fork.py](play_fork.py)。
父进程增加了 waitpid 之后会一直等待子进程执行完毕。

### 父子如何同步合作
#### 为什么在父进程关闭 connection，而在子进程关闭 socket？
```python
def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        pid = os.fork()  # 好戏在这里，创建子进程处理新连接
        if pid < 0:  # fork error
            return
        if pid > 0:  # parent process
            conn.close()  # 关闭父进程的客户端套接字引用
            continue
        if pid == 0:
            sock.close()  # 关闭子进程的服务器套接字引用
            handle_conn(conn, addr, handlers)
            break  # 处理完后一定要退出循环，不然子进程也会继续去 accept 连接
```
##### 我的猜测
我的初步印象理解是，fork 之后 父进程与子进程拥有相同的资源，例如 socket 和 connection。
- 父进程关闭 connection 是因为 父进程负责从 socket 接受请求，产生新的 connection，
并把connection 传递给子进程，让子进程具体去处理每一个 connection。
- 子进程关闭 socket 是因为 统一只让父进程通过socket产生新的 connection来 dispatch 分发任务，
子进程只需要 connection 即可。

##### 作者的解释
因为进程 fork 之后，套接字会复制一份到子进程，这时父子进程将会各有自己的套接字引用指向内核的同一份套接字对象，套接字的引用计数为2。

对套接字进程 close，并不是说就是关闭套接字，其本质上只是将内核套接字对象的引用计数减一。只有当引用计数减为零时，才会关闭套接字。

如果没有上述逻辑就会导致服务器套接字引用计数不断增长，同时客户端套接字对象也得不到即时回收，这便是传说中的资源泄露。



## References

- [os.waitpid example](https://www.delftstack.com/api/python/python-os-waitpid/#google_vignette)