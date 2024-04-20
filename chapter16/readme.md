# Chapter 16 Notes

## 小册子内容
### 杀死子进程
- os.kill(pid, signal.SIGKILL) signal of kill 杀死
  - SIGKILL 信号比较暴力，对方进程会立即 crash，进程无法为 SIGKILL 信号设置处理函数。
  - SIGKILL 当你使用 kill -9 杀死进程时，进程会收到信号。此信号的处理函数无法覆盖，进程收到此信号会立即暴力退出。

- os.kill(pid, signal.SIGTERM) signal of terminate 终止
  - 通过 SIGTERM 信号温柔地通知对方退出，只要对方进程设置了信号处理函数，就可以在退出之前执行一些清理工作。
  - SIGTERM 当你使用不带参数的 kill 指令杀死进程时，进程会收到该信号。此信号默认行为也是退出进程，但是允许用户自定义信号处理函数。

- os.kill(pid, signal.SIGINT) signal of interrupt 打断 暂停
  - KeyboardInterrupt = ctrl+c
  - SIGINT 信号温柔地通知对方退出，只要对方进程设置了信号处理函数，就可以在退出之前执行一些清理工作。
  - 参见 [play_signal.py:play_sigint](play_signal.py)

- SIGCHLD signal of child 
  - 子进程退出时，父进程会收到此信号。
  - 当子进程退出后，父进程必须通过 waitpid 来收割子进程，否则子进程将成为僵尸进程，直到父进程也退出了，其资源才会彻底释放。

- SIGTSTP signal of stop
  - ctrl+z 
  - 参见 [play_signal.py:play_sigtstp](play_signal.py)

### 收割子进程
收割子进程使用os.waitpid(pid, options)系统调用，
- 可以提供具体 pid 来收割指定子进程，
- 也可以通过参数 pid=-1 来收割任意子进程。
- options 如果是 0，就表示阻塞等待子进程结束才会返回，
- options 如果是 WNOHANG 就表示非阻塞，有,就返回指定进程的 pid，没有,就返回 0。
- 如果指定 pid 进程不存在或者没有子进程可以收割，就会抛出 OSError(errno.ECHILD)
- 如果 waitpid 被其它信号打断，就会抛出 OSError(errno.EINTR)，这个时候可以选择重试。

### 信号连续打断
当我们正在执行一个信号处理函数时，可能又收到另外一个信号，该信号会打断当前正在执行的信号处理函数。

如果信号处理函数中 waitpid 正在执行，这个时候突然来了一个 SIGINT 信号，
那么待 SIGINT 信号处理函数执行完毕后返回到原来的 waitpid 调用时，waitpid 将会爆出 OSError 异常，
也就是 waitpid 调用被打断了。

我们通过检查异常对象里面的错误类型，来决定是否要继续重试。

- 如果异常类型是 errno.EINTR，就可以继续重试 waitpid，
- 如果是 errno.ECHILD，说明目标子进程已经结束了，
- 遇到其它类型应该向上抛出异常。至于什么是其它异常，这个是没有具体定义的，而且是不应该出现的。

### 错误码
```
errno.EPERM
Operation not permitted  # 操作不允许

errno.ENOENT
No such file or directory  # 文件没找到

errno.ESRCH
No such process  # 进程未找到

errno.EINTR
Interrupted system call  # 调用被打断

errno.EIO
I/O error  # I/O 错误

errno.ENXIO
No such device or address  # 设备未找到

errno.E2BIG
Arg list too long  # 调用参数太多

errno.ENOEXEC¶
Exec format error  # exec 调用二进制文件格式错误

errno.EBADF
Bad file number  # 文件描述符错误

errno.ECHILD
No child processes  # 子进程不存在， errno.ECHILD 在 waitpid 收割子进程时，目标进程不存在，就会有这样的错误。

errno.EAGAIN
Try again  # I/O 操作被打断，告知 I/O 操作重试

```

### 服务发现
ZooKeeper 的节点信息以树状结构存储在内存中。每个节点内部可以存储一个字节串，节点用于服务发现时存储服务器的地址信息。

#### 顺序节点
ZooKeeper 支持顺序节点 (sequence)，它可以在节点名称后面自动追加自增 id，避免节点名称重复。
在服务发现中会有多个子节点，使用顺序节点可以很方便地增加子节点。

#### 临时节点
ZooKeeper 支持临时节点 (ephemeral)，在会话结束时，临时节点会自动释放。
之所以会用到临时节点是因为 ZooKeeper 的会话支持连接断开重连。
短时间的连接断开并不会立即删除内存会话，而是有个过期时间，时间一到，会话会自动过期。
可以显式发送会话结束指令强制关闭会话，
如果客户端进程突然 crash 掉，来不及发送会话关闭指令，ZooKeeper 将通过会话自动过期机制关闭会话。
